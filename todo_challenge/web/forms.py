from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class TaskForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        label="Título",
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-sm",
            "placeholder": "Ej: Comprar pan",
            "autocomplete": "off",
            "autofocus": "autofocus",
        }),
    )
    description = forms.CharField(
        required=False,
        label="Descripción",
        widget=forms.Textarea(attrs={
            "class": "form-control form-control-sm",
            "rows": 3,
            "placeholder": "Detalles (opcional)",
        }),
    )

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("El título no puede estar vacío.")
        return title


class TaskUpdateForm(TaskForm):
    completed = forms.BooleanField(
        required=False,
        label="Completada",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


class TaskFilterForm(forms.Form):
    completed = forms.ChoiceField(
        required=False,
        choices=(("", "Todas"), ("true", "Completadas"), ("false", "Pendientes")),
        label="Completada",
        widget=forms.Select(attrs={"class": "form-select form-select-sm"})
    )
    created_at_after = forms.DateField(
        required=False,
        label="Creada desde",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control form-control-sm"})
    )
    created_at_before = forms.DateField(
        required=False,
        label="Creada hasta",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control form-control-sm"})
    )
    updated_at_after = forms.DateField(
        required=False,
        label="Actualizada desde",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control form-control-sm"})
    )
    updated_at_before = forms.DateField(
        required=False,
        label="Actualizada hasta",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control form-control-sm"})
    )