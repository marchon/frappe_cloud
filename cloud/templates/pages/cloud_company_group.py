# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies


def is_company_admin(user, company):
	return company in list_admin_companies(user)


def get_context(context):
	name = frappe.form_dict.group or frappe.form_dict.name
	if not name:
		frappe.local.flags.redirect_location = "/me"
		raise frappe.Redirect

	context.no_cache = 1
	context.show_sidebar = True
	doc = frappe.get_doc('Cloud Company Group', name)
	is_admin = is_company_admin(frappe.session.user, doc.company)

	doc.has_permission('read')

	if is_admin:
		doc.users = get_users(doc.name, start=0, search=frappe.form_dict.get("search"))

	context.is_admin = is_admin
	context.parents = [{"title": doc.group_name, "route": "/cloud_companies/" + doc.company}]
	context.doc = doc
	"""
	context.parents = [
		{"title": _("Back"), "route": frappe.get_request_header("referer")},
		{"title": doc.parent, "route": "/cloud_companies/" + doc.parent}
	]
	"""


def get_users(group, start=0, search=None):
	filters = {"parent": group}
	if search:
		filters["user"] = ("like", "%{0}%".format(search))

	return frappe.get_all("Cloud Company GroupUser", filters=filters,
		fields=["user", "role", "modified", "creation"],
		limit_start=start, limit_page_length=10)

