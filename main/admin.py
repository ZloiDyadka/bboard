from django.contrib import admin
from .models import AdvUser
import datetime
from .utilities import send_activation_notification
from .models import SuperRubric, SubRubric
from .forms import SubRubrickForm
from .models import Bb, AdditionalImage

class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage

class BbAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', 'content', 'author', 'created_at')
    fields = (('rubric', 'author'), 'title', 'content', 'price', 'contacts', 'image', 'is_active')
    inlines = (AdditionalImageInline,)

admin.site.register(Bb, BbAdmin)

class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubrickForm

admin.site.register(SubRubric, SubRubricAdmin)

class SubRubricInLine(admin.TabularInline):
    model = SubRubric

class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ('super_rubric',)
    inlines = (SubRubricInLine,)

admin.site.register(SuperRubric, SuperRubricAdmin)

def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'письма с требованиями отправлены')
    send_activation_notifications.short_description = \
    'отправка писем с требованием активации'

class NonactivstedFilter(admin.SimpleListFilter):
    title = 'прощли активацию'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
            ('activated', 'прошли'),
            ('threedays', 'не прошли более 3 дней'),
            ('week', 'не прошли более недели'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined_date_lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_activ=False, is_activated=False, date_joined_date_lt=d)

class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (NonactivstedFilter,)
    fields = (('username', 'email'), ('first_name', 'last_name'),
              ('send_messages', 'is_active', 'is_activated'),
              ('is_staff', 'is_superuser'),
              'groups', 'user_permissions',
              ('last_login', 'date_joined'))
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)

admin.site.register(AdvUser, AdvUserAdmin)