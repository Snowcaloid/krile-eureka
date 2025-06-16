

from data_providers._base import BaseProvider
from models.message_assignment import MessageAssignmentStruct


class MessageAssignmentsProvider(BaseProvider[MessageAssignmentStruct]):
    """Provider for Message Assignments."""

    def struct_type(self) -> type[MessageAssignmentStruct]:
        return MessageAssignmentStruct
