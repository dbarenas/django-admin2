from django import template
from django.db.models.fields import FieldDoesNotExist

register = template.Library()

from .. import utils


@register.filter
def admin2_urlname(view, action):
    """
    Converts the view and the specified action into a valid namespaced URLConf name.
    """
    return utils.admin2_urlname(view, action)


@register.filter
def model_app_label(obj):
    """
    Returns the app label of a model instance or class.
    """
    return utils.model_app_label(obj)


@register.filter
def model_verbose_name(obj):
    """
    Returns the verbose name of a model instance or class.
    """
    return utils.model_verbose_name(obj)


@register.filter
def model_verbose_name_plural(obj):
    """
    Returns the pluralized verbose name of a model instance or class.
    """
    return utils.model_verbose_name_plural(obj)


@register.filter
def model_attr_verbose_name(obj, attr):
    """
    Returns the verbose name of a model field or method.
    """
    try:
        return utils.model_field_verbose_name(obj, attr)
    except FieldDoesNotExist:
        return utils.model_method_verbose_name(obj, attr)


@register.filter
def formset_visible_fieldlist(formset):
    """
    Returns the labels of a formset's visible fields as an array.
    """
    return [f.label for f in formset.forms[0].visible_fields()]


@register.filter
def for_admin(permissions, admin):
    """
    Only useful in the permission handling. This filter binds a new admin to
    the permission handler to allow checking views of an arbitrary admin.
    """
    # some permission check has failed earlier, so we don't bother trying to
    # bind a new admin to it.
    if permissions == '':
        return permissions
    return permissions.bind_admin(admin)


@register.filter
def for_view(permissions, view):
    """
    Only useful in the permission handling. This filter binds a new view to
    the permission handler to check for view names that are not known during
    template compile time.
    """
    # some permission check has failed earlier, so we don't bother trying to
    # bind a new admin to it.
    if permissions == '':
        return permissions
    return permissions.bind_view(view)


@register.filter
def for_object(permissions, obj):
    """
    Only useful in the permission handling. This filter binds a new object to
    the permission handler to check for object-level permissions.
    """
    # some permission check has failed earlier, so we don't bother trying to
    # bind a new object to it.
    if permissions == '':
        return permissions
    return permissions.bind_object(obj)


@register.simple_tag(takes_context=True)
def render(context, model_instance, attribute_name):
    """
    This filter applies all renderers specified in admin2.py to the field.
    """
    value = utils.get_attr(model_instance, attribute_name)

    # Get renderer
    admin = context['view'].model_admin
    renderer = admin.field_renderers.get(attribute_name)
    if not renderer:
        return value

    # Apply renderer and return value
    try:
        field = model_instance._meta.get_field_by_name(attribute_name)[0]
    except FieldDoesNotExist:
        # There is no field with the specified name.
        # It must be a method instead.
        field = None
    return renderer(value, field)
