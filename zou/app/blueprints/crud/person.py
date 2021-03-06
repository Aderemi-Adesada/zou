from flask import abort, request
from flask_jwt_extended import jwt_required

from zou.app.models.person import Person
from zou.app.services import persons_service, deletion_service
from zou.app.utils import permissions

from .base import BaseModelsResource, BaseModelResource

from zou.app.mixin import ArgsMixin


class PersonsResource(BaseModelsResource):
    def __init__(self):
        BaseModelsResource.__init__(self, Person)

    def all_entries(self, query=None, relations=False):
        if query is None:
            query = self.model.query

        if permissions.has_manager_permissions():
            if request.args.get("with_pass_hash") == "true":
                return [person.serialize() for person in query.all()]
            else:
                return [person.serialize_safe() for person in query.all()]
        else:
            return [person.present_minimal() for person in query.all()]

    def post(self):
        abort(405)

    def check_read_permissions(self):
        return True


class PersonResource(BaseModelResource, ArgsMixin):
    def __init__(self):
        BaseModelResource.__init__(self, Person)
        self.protected_fields += ["password"]

    def check_read_permissions(self, instance):
        return True

    def check_update_permissions(self, instance_dict, data):
        if instance_dict["id"] != persons_service.get_current_user()["id"]:
            self.check_escalation_permissions(instance_dict, data)
        else:
            data.pop("role", None)
        return instance_dict

    def check_delete_permissions(self, instance_dict):
        if instance_dict["id"] == persons_service.get_current_user()["id"]:
            raise permissions.PermissionDenied
        self.check_escalation_permissions(instance_dict)
        return instance_dict

    def check_escalation_permissions(self, instance_dict, data=None):
        if permissions.admin_permission.can():
            return True
        else:
            raise permissions.PermissionDenied

    def serialize_instance(self, instance):
        if permissions.has_manager_permissions():
            return instance.serialize_safe()
        else:
            return instance.present_minimal()

    def post_update(self, instance_dict):
        persons_service.clear_person_cache()
        return instance_dict

    def post_delete(self, instance_dict):
        persons_service.clear_person_cache()
        return instance_dict

    def update_data(self, data, instance_id):
        if "password" in data:
            del data["password"]
        return data

    @jwt_required
    def delete(self, instance_id):
        """
        Delete a person corresponding at given ID and return it as a JSON
        object.
        """
        force = self.get_force()
        person = self.get_model_or_404(instance_id)
        person_dict = person.serialize()
        self.check_delete_permissions(person_dict)
        self.pre_delete(person_dict)
        deletion_service.remove_person(person_dict["id"], force=force)
        self.emit_delete_event(person_dict)
        self.post_delete(person_dict)
        return "", 204
