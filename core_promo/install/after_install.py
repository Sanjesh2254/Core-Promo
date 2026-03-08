from core_promo.core_promo.customization.task.custom_field import create_task_types


def after_install():
	create_task_types()
