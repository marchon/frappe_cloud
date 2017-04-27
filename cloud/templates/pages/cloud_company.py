# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups
from cloud.cloud.doctype.cloud_company.cloud_company import list_groups_obj


def get_context(context):
	name = frappe.form_dict.company or frappe.form_dict.name
	context.group_hack_url = frappe.form_dict.group_hack_url
	context.user_hack_url = frappe.form_dict.user_hack_url

	if not name:
		name = frappe.get_value("Cloud Employee", frappe.session.user, "company")

	if not name:
		frappe.local.flags.redirect_location = "/me"
		raise frappe.Redirect

	context.no_cache = 1
	context.show_sidebar = True
	#context.no_breadcrumbs = True

	company = frappe.get_doc('Cloud Company', name)
	company.has_permission('read')

	groups = list_groups_obj(name)

	if company.get('admin') == frappe.session.user:
		company.users = get_users(company.name, start=0, search=frappe.form_dict.get("search"))
		context.is_admin = True
		company.groups = groups
	else:
		user_groups = [d.name for d in list_user_groups(frappe.session.user)]
		company.groups = [g for g in groups if g.name in user_groups]

	context.doc = company
	"""
	context.parents = [
		{"title": _("Back"), "route": frappe.get_request_header("referer")},
		{"title": _("Cloud Companies"), "route": "/cloud_companies"}
	]
	"""

def get_users(company, start=0, search=None):
	filters = {"company": company}
	if search:
		filters["user"] = ("like", "%{0}%".format(search))

	users = frappe.get_all("Cloud Employee", filters=filters,
		fields=["name", "company", "modified", "creation"],
		limit_start=start, limit_page_length=10)

	return users
