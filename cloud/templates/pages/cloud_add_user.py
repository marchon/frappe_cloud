# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from cloud.cloud.doctype.cloud_company.cloud_company import list_users, get_domain
from cloud.cloud.doctype.cloud_employee.cloud_employee import add_employee


def is_company_admin(user, company):
	return frappe.db.get_value("Cloud Company", {"name": company, "admin": user}, "admin")


def list_users_by_domain(domain):
	return frappe.get_all("User",
		filters={"email": ("like", "%@{0}".format(domain))},
		fields=["name", "full_name", "enabled", "email", "creation"])


def list_possible_users(company):
	domain = get_domain(company)
	users = list_users_by_domain(domain)
	employees = list_users(company)
	return [user for user in users if user.name not in employees]


def get_context(context):
	company = frappe.form_dict.company
	if frappe.form_dict.user:
		add_employee(frappe.form_dict.user, company)
		frappe.local.flags.redirect_location = "/cloud_add_user?company=" + company
		raise frappe.Redirect

	user = frappe.session.user

	if not company:
		raise frappe.ValidationError(_("You need specified Cloud Enterprise"))

	user_roles = frappe.get_roles(frappe.session.user)
	if 'Company Admin' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError("Your account is not an Cloud User!")

	if not (is_company_admin(user, company) or 'Company Admin' in user_roles):
		raise frappe.PermissionError

	context.no_cache = 1
	context.show_sidebar = True

	possible_users = list_possible_users(company)

	context.parents = [{"title": company, "route": "/cloud_companies/" + company}]
	context.doc = {
		"company": company,
		"possible_users": possible_users
	}
