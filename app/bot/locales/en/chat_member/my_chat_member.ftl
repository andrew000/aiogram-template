my_chat_member-promoted_transition =
    ❤️ Thank you for promoting me to an administrator!

    💬 For full functionality, I need the following rights:
    { $can_delete_messages ->
        [1] ✅ Delete messages
       *[other] ❌ Delete messages
    }
    { $can_restrict_members ->
        [1] ✅ Restrict members
       *[other] ❌ Restrict members
    }
    { $can_invite_users ->
        [1] ✅ Invite users
       *[other] ❌ Invite users
    }
my_chat_member-join_transition =
    ❤️ Thank you for adding me to the chat.

    💬 For full functionality, I need the following rights:
    { $can_delete_messages ->
        [1] ✅ Delete messages
       *[other] ❌ Delete messages
    }
    { $can_restrict_members ->
        [1] ✅ Restrict members
       *[other] ❌ Restrict members
    }
    { $can_invite_users ->
        [1] ✅ Invite users
       *[other] ❌ Invite users
    }
my_chat_member-demoted_transition =
    My administrator rights have been revoked.

    I will continue to work in the chat, but with limited capabilities.
