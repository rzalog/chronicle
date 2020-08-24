#!/usr/bin/env python3
# Copyright 2020 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Examples of integrations with other products.

Upon receiving rule notifications from stream_rule_notifications, the customers
will likely want to integrate with other platforms.
Examples of such integrations are below.


These examples are for python3.
"""

import collections
import json
import logging
import requests
from datetime import datetime

# WEBHOOK_URL is used for chat ops integrations. The example shown below features
# slack webhooks, but will also work with google chat webhooks.
# The slack integration is disabled when WEBHOOK_URL is None.
# To try the slack webhook integration, populate WEBHOOK_URL with a string, e.g.
# WEBHOOK_URL = "https://hooks.slack.com/services/yourWebhookHere"
WEBHOOK_URL = None

# Notification batches might have lots of notifications. We want to avoid
# dumping lots of UDM text into the terminal output or the slack chat room.
# For all notification batches, we'll summarize the notification batch (e.g. how
# many notifications came from which rule/jobs).
# However, for notification batches with more notifications than
# MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL,
# we'll omit reporting on each notification individually.
# Increase this if you're fine with noisier outputs.
MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL = 100

# See https://api.slack.com/changelog/2018-04-truncating-really-long-messages
# Long messages will be truncated after 40k characters (resulting in data being omitted).
# Additionally, long messages will be split into multiple messages, which
# will interrupt formatting blocks such as triple backticks, ```.
# To avoid both of the above, we can send multiple smaller messages.
# Each message posted will contain at most this many rule notifications.
NOTIFICATIONS_PER_WEBHOOK_MESSAGE = 3


def print_notifications(notification_batch):
  """Print a set of notifications.

  Args:
    notification_batch: Contains a list of notifications in
      notification_batch["notifications"] if notifications are present, and a
      continuation time in notification_batch["continuationTime"].

  Returns:
    None
  """
  time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  if "notifications" in notification_batch and notification_batch["notifications"]:
    print("[{}] Received new notifications.".format(time))
    print(json.dumps(notification_batch, indent="  "))
  else:
    print("[{}] No new notifications at this time.".format(time))


def slack_webhook(notification_batch):
  """Process one notification batch from stream_rule_notifications.

  Forms a textual report to summarize notifications and then sends the report to
  a slack webhook. This function requires WEBHOOK_URL to be set. Otherwise it
  will return immediately.

  Args:
    notification_batch: Contains a list of notifications in
      notification_batch["notifications"] if notifications are present, and a
      continuation time in notification_batch["continuationTime"].

  Returns:
    None
  """
  if not WEBHOOK_URL:
    return
  if "notifications" not in notification_batch or not notification_batch["notifications"]:
    return

  notifications = notification_batch["notifications"]
  continuation_time = notification_batch["continuationTime"]
  batch_size = len(notifications)

  report_lines = []
  report_lines.append(
      "Got stream response with continuationTime {}, containing {} notifications."
      .format(continuation_time, batch_size))

  # Aggregate by each (Rule/Operation), and list the count of
  # associated notifications. Recall that the server's notifications
  # ARE NOT AGGREGATED, and are NOT SORTED in any particular grouping/order.
  # This aggregation is done entirely within this python client code.
  report_lines.append("Summary of notifications:")
  # notif_metadatas is a list of the metadata (i.e., RuleID, rule name, and
  # operation name) from all the notifications.
  notif_metadatas = [
      tuple((notif["rule"], notif["ruleId"], notif["operation"]))
      for notif in notifications
  ]
  for notif_metadata, count in collections.Counter(notif_metadatas).items():
    report_lines.append(
        "\t{} notifications from Rule `{}` (`{}`), Operation `{}`".format(
            count, notif_metadata[0], notif_metadata[1], notif_metadata[2]))

  if batch_size > MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL:
    # Avoid flooding our output channels.
    report_lines.append(
        "Omitting UDM events because more than {} total notifications were received."
        .format(MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL))
    report_lines.append("To get results for an operation listed above, "
                        "call list_results and pass in that operation.")
    report_lines.append("")
    report_string = "\n".join(report_lines)
    if WEBHOOK_URL:
      requests.post(WEBHOOK_URL, json={"text": report_string})
  else:
    # Output each notification's metadata (Rule and Operation IDs), and its UDM event.
    report_lines.append("UDM events from notifications are listed below:")
    for idx, notif in enumerate(notifications):
      report_lines.append("{}) from Rule `{}` (`{}`), Operation `{}`".format(
          idx, notif["rule"], notif["ruleId"], notif["operation"]))
      report_lines.append("```{}```".format(
          json.dumps(notif["result"]["match"], indent="\t")))

      if idx % NOTIFICATIONS_PER_WEBHOOK_MESSAGE == 0 or idx == batch_size - 1:
        # Construct a report string, then clear out report_lines so the
        # next iterations can start building an new list.
        report_string = "\n".join(report_lines)
        report_lines.clear()
        report_lines.append("")

        requests.post(WEBHOOK_URL, json={"text": report_string})
