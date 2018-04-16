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

from iam.models import Organization, Project, User


def test_db(db):
    organization = Organization(name='FooOrg')
    project = Project(name='FooProject', organization=organization)
    user = User(first_name='Foo', last_name='Bar', email='foo@bar.dk')
    user.set_password('hunter2')
    db.session.add(organization)
    db.session.add(project)
    db.session.add(user)
    db.session.commit()
