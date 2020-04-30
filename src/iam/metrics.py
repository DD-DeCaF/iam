# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability, DTU.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Define the metrics used throughout the application."""

import prometheus_client


# USER_COUNT: The current number of users in the database
# labels:
#   service: The current service (always 'iam')
#   environment: The current runtime environment ('production' or 'staging')
USER_COUNT = prometheus_client.Gauge(
    "decaf_user_count",
    "The current number of users in the database",
    ["service", "environment"],
)


# ORGANIZATION_COUNT: The current number of users in the database
# labels:
#   service: The current service (always 'iam')
#   environment: The current runtime environment ('production' or 'staging')
ORGANIZATION_COUNT = prometheus_client.Gauge(
    "decaf_organization_count",
    "The current number of users in the database",
    ["service", "environment"],
)


# PROJECT_COUNT: The current number of projects in the database
# labels:
#   service: The current service (always 'iam')
#   environment: The current runtime environment ('production' or 'staging')
PROJECT_COUNT = prometheus_client.Gauge(
    "decaf_project_count",
    "The current number of projects in the database",
    ["service", "environment"],
)
