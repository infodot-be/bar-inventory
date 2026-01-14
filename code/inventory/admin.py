from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django import forms
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Location, UnitType, Beverage, BEVERAGE_COLORS
from .tokens import location_token_generator


class LocationResource(resources.ModelResource):
    class Meta:
        model = Location
        fields = ('id', 'name', 'description', 'is_active', 'user')


class UnitTypeResource(resources.ModelResource):
    class Meta:
        model = UnitType
        fields = ('id', 'name', 'quantity')


class BeverageResource(resources.ModelResource):
    class Meta:
        model = Beverage
        fields = ('id', 'name', 'description', 'unit_type', 'liters_per_unit', 'alarm_minimum', 'color', 'is_active')


@admin.register(Location)
class LocationAdmin(ImportExportModelAdmin):
    resource_class = LocationResource
    list_display = ['name', 'assigned_user', 'token_display', 'is_active', 'beverage_count', 'token_link']
    list_filter = ['is_active']
    search_fields = ['name', 'description', 'user__username']

    def beverage_count(self, obj):
        return obj.beverages.count()
    beverage_count.short_description = 'Beverages'

    def assigned_user(self, obj):
        if obj.user:
            return obj.user.username
        return '-'
    assigned_user.short_description = 'Assigned User'

    def token_display(self, obj):
        if obj.user:
            uidb64 = urlsafe_base64_encode(force_bytes(obj.user.pk))
            token = location_token_generator.make_token(obj.user)
            return format_html(
                '<code style="font-size: 0.85em; background: #f4f4f4; padding: 2px 6px; border-radius: 3px;">{}/{}</code>',
                uidb64, token
            )
        return '-'
    token_display.short_description = 'Token'

    def token_link(self, obj):
        if obj.user:
            url = reverse('inventory:generate_token', args=[obj.id])
            return format_html('<a href="{}" class="button">Generate Token Link</a>', url)
        return '-'
    token_link.short_description = 'Token Link'


@admin.register(UnitType)
class UnitTypeAdmin(ImportExportModelAdmin):
    resource_class = UnitTypeResource
    list_display = ['name', 'quantity']
    ordering = ['name', 'quantity']


class ColorSelectWidget(forms.Select):
    """Custom widget to display color previews in dropdown."""
    template_name = 'admin/widgets/color_select.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            option['attrs']['data-color'] = value
        return option


class BeverageAdminForm(forms.ModelForm):
    """Custom form for Beverage with color selection."""
    color = forms.ChoiceField(
        choices=[(color, color) for color in BEVERAGE_COLORS],
        widget=ColorSelectWidget,
        help_text="Select a color for chart display"
    )

    class Meta:
        model = Beverage
        fields = '__all__'

    class Media:
        css = {
            'all': ('admin/css/color_select.css',)
        }
        js = ('admin/js/color_select.js',)


@admin.register(Beverage)
class BeverageAdmin(ImportExportModelAdmin):
    resource_class = BeverageResource
    form = BeverageAdminForm
    list_display = ['name', 'color_display', 'unit_type', 'liters_per_unit', 'is_active', 'location_count']
    list_filter = ['is_active', 'unit_type']
    search_fields = ['name', 'description']
    filter_horizontal = ['available_locations']

    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background-color: {}; border-radius: 50%; border: 1px solid #ccc;"></span>',
            obj.color
        )
    color_display.short_description = 'Color'

    def location_count(self, obj):
        return obj.available_locations.count()
    location_count.short_description = 'Locations'


# Unregister the default User admin
admin.site.unregister(User)

# Custom User admin with token login display
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'assigned_location', 'token_login_link', 'is_staff']

    def assigned_location(self, obj):
        if hasattr(obj, 'location') and obj.location:
            return obj.location.name
        return '-'
    assigned_location.short_description = 'Location'

    def token_login_link(self, obj):
        uidb64 = urlsafe_base64_encode(force_bytes(obj.pk))
        token = location_token_generator.make_token(obj)
        token_url = f'/token-login/{uidb64}/{token}/'

        return format_html(
            '<a href="{}" target="_blank" style="font-size: 0.85em;">{}</a>',
            token_url,
            token_url
        )
    token_login_link.short_description = 'Token Login Link'
