import frappe
from frappe.utils import add_to_date
from datetime import datetime, timedelta


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_available_units(doctype, txt, searchfield, start, page_len, filters):
    # print(filters)
    if not 'start_date' in filters:
        frappe.throw("Start Date is Missing")
    if not 'start_time' in filters:
        frappe.throw("Start Time is Missing")
    date_str = filters['start_date']
    time_str = filters['start_time']
    duration_minutes = filters['duration']
    date_time_str = f'{date_str} {time_str}'
    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    duration = timedelta(minutes=duration_minutes)
    end_date_time_obj = date_time_obj + duration
    end_time_str = end_date_time_obj.strftime('%H:%M:%S')
    unit1 = frappe.db.sql('''select custom_health_service_unit from `tabTherapy Session` where start_date = '{0}' and 
                  start_time >= '{1}' and  start_time < '{2}' and
                 custom_health_service_unit is not null and 
                name != '{3}' and custom_health_service_unit like %(txt)s '''.format(date_str, time_str, end_time_str,filters['name']),{
			"txt": "%{0}%".format(txt)
		},as_dict=1)
    unit1 = [i["custom_health_service_unit"] for i in unit1]
    # print(unit1)
    unit2 = frappe.db.sql('''select service_unit from `tabTherapy Type Service Units` where parenttype = "Therapy Type" 
                  and parent = "{0}" and service_unit like %(txt)s '''.format(filters['therapy_type']),{"txt": "%{0}%".format(txt)},as_dict=1)
    unit2 = [i["service_unit"] for i in unit2]
    # print(unit2)
    result = list(set(list(set(unit2) - set(unit1))+list(set(unit1) - set(unit2))))
    # print(result)
    if unit1 and not unit2:
        return (())
    if not len(result) or not len(result[0]):
        return (())
    return [[val,val] for val in result]