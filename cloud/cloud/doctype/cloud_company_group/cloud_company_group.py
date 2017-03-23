# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _dict
from frappe.model.document import Document
from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies

class CloudCompanyGroup(Document):
	pass


def get_permission_query_conditions(user):
	if 'Cloud Manager' in frappe.get_roles(user):
		return ""

	ent_list = [d[0] for d in frappe.db.get_values("Cloud Company", {"admin": user}, "name")]

	return """(`tabCloud Company Group`.company in ({user_ents}))""".format(
		user_ents='"' + '", "'.join(ent_list) + '"')


def has_permission(doc, ptype, user):
	if 'Cloud Manager' in frappe.get_roles(user):
		return True

	if frappe.get_value('Cloud Company', {'admin': user, 'name': doc.company}):
		return True

	return False


def list_user_groups(user):
	groups = []
	for d in frappe.db.get_values("Cloud Company GroupUser", {"user": user}, ["parent", "role"]):
		groups.append(_dict({"group": d[0], "role": d[1], "user": user}))
	for comp in list_admin_companies(user):
		for d in frappe.db.get_values("Cloud Company Group", {"company": comp}, "name"):
			groups.append(_dict({"group": d[0], "role": "admin", "user": user}))

	return groups


def list_users(group):
	users = []
	for d in frappe.db.get_values("Cloud Company GroupUser", {"parent": group}, ["user", "role"]):
		users.append(_dict({"user": d[0], "role": d[1], "group": group}))

	return users

def get_company(group):
	return frappe.db.get_value("Cloud Company Group", group, "company")