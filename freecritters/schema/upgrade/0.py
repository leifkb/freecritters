run_sql()

conn.execute('INSERT INTO roles(label, name) VALUES(%s, %s)', (u'default', u'User'))
default_role_id, = conn.execute("SELECT currval('roles_role_id_seq')").get_one()

permissions_to_add = [
    (u'edit_profile', u'Edit profile', u'Allows profile editing.'),
    (u'view_mail', u'View mail', u'Allows mail to be viewed.'),
    (u'send_mail', u'Send mail',
     u'Allows mail to be sent and replied to.'),
    (u'delete_mail', u'Delete mail', u'Allows mail to be deleted.'),
    (u'create_pet', u'Create pet', u'Allows pets to be created.')
]

for data in permissions_to_add:
    conn.execute('INSERT INTO permissions(label, title, description) VALUES(%s, %s, %s)', data)
    permission_id, = conn.execute("SELECT currval('permissions_permission_id_seq')").get_one()
    conn.execute('INSERT INTO role_permissions(role_id, permission_id) VALUES(%s, %s)', (default_role_id, permission_id))