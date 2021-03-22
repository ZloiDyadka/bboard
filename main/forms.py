from django import forms

from .models import AdvUser

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .apps import user_registered
from .models import SuperRubric, SubRubric

from django.forms import inlineformset_factory

from .models import Bb, AdditionalImage

"""Здесь описываются формы"""



class BbForm(forms.ModelForm):
    class Meta:
        model = Bb
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}


AIFormSet = inlineformset_factory(Bb, AdditionalImage, fields='__all__')


class SubRubricForm(forms.ModelForm):

    """ поле надрубрики, обязательно """

    super_rubric = forms.ModelChoiceField(queryset=SuperRubric.objects.all(), empty_label=None, label='надрубрика',
                                          required=True)

    class Meta:
        model = SubRubric
        fields = '__all__'


class RegisterUserForm(forms.ModelForm):

    """ форма занесения сведений о новом пользователе """

    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль(повторно)', widget=forms.PasswordInput,
                                help_text='Введите тот же самый пароль еще раз для проверки')

    def clean_passwordl1(self):

        """ Валидация пароля """

        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        """ проверка на совпадения паролей друг с другом """
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('введенные пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        """ при сохранении новый пользователь по умолчанию не активирован значит не может выполнить вход """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registered.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'send_messages')


class ChangeUserInfoForm(forms.ModelForm):

    """Форма связаная с AdvUser для ввода основных данных"""

    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_messages')


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label='')
