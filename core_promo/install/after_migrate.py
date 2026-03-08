from core_promo.core_promo.customization.task.custom_field import create_task_types


def after_migrate():
	create_task_types()
