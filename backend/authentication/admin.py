"""Admin configuration for authentication."""

from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm


class EmailAdminAuthenticationForm(AdminAuthenticationForm):
    """Display the admin login username field as an email field."""

    def __init__(self, *args, **kwargs):
        """Label the username field as email."""

        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"


admin.site.login_form = EmailAdminAuthenticationForm
