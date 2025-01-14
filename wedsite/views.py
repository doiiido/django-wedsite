# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.edit import FormView, UpdateView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.views import (
    redirect_to_login, RedirectURLMixin as SuccessURLAllowedHostsMixin)
from django.contrib.auth import (
    authenticate, login)
from django.contrib.auth.models import User
from wedsite.forms import CreateUserForm, RSVPPersonFormSet, RSVPForm
from wedsite.models import Profile, RSVP
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.http import HttpResponseRedirect
from wedsite.conf import settings

class StaticView(View):
    """
    Basic static view. Shows a template back

    Will redirect to login page if the user isn't authenticated, otherwise will
    allow them to view the requested page.

    """
    template = None

    def get(self, request):
        if request.user.is_authenticated or (request.get_full_path() == reverse('index')):
            return render(request, "wedding/pages/" + self.template, {})
        else:
            return redirect_to_login(request.get_full_path())

class StaticViewNoAuth(View):
    """
    Basic static view. Shows a template back
    """
    template = None

    def get(self, request):
        return render(request, "wedding/pages/" + self.template, {})

class RSVPView(View):
    """
    RSVP View.

    Handles the form data for RSVPs.

    """
    def get_object(self, queryset=None):
        try:
            return self.request.user.profile.rsvp
        except RSVP.DoesNotExist:
            return None

    def post(self, request):
        if request.user.is_authenticated:
            rsvp = self.get_object()

            # Handle the RSVP update itself
            rsvp_form = RSVPForm(request.POST, request.FILES, instance=rsvp, prefix='rsvp')

            # Handle the RSVP Persons
            formset = RSVPPersonFormSet(request.POST, request.FILES, instance=rsvp, prefix='people')

            if formset.is_valid and rsvp_form.is_valid():
                try:
                    formset.save()
                    rsvp_form.save()
                    return HttpResponseRedirect(request.get_full_path() + '?updated=y')
                except ValueError:
                    pass



            return render(request, 'wedding/pages/rsvp.html', {'formset': formset})
        else:
            return redirect_to_login(request.get_full_path())

    def get(self, request):
        if request.user.is_authenticated:
            rsvp = self.get_object()
            updated = True if (request.GET.get('updated', '') == 'y') else False
            new_account = True if (request.GET.get('new_account', '') == 'y') else False
            formset = RSVPPersonFormSet(instance=rsvp, prefix='people') if rsvp else []

            # Need to make the formset read-only if RSVPs are already locked.
            if not settings.WEDSITE_JSON['rsvp']['active']:
                for form in formset:
                    for field in form.fields:
                        form.fields[field].disabled = True

            rsvp_form = RSVPForm(instance=rsvp, prefix='rsvp') if rsvp else None
            return render(request, 'wedding/pages/rsvp.html',
                {
                    'formset': formset,
                    'rsvp_form': rsvp_form,
                    'updated': updated,
                    'new_account': new_account
                }
            )
        else:
            return redirect_to_login(request.get_full_path())


class CreateAccountView(SuccessURLAllowedHostsMixin, FormView):
    """
    Account creation view. Will take a name, street address,
    email address and password and will create a new user if it can find
    a free RSVP that agrees with the user's info.
    """
    form_class = CreateUserForm
    success_url = "/rsvp?new_account=y"
    template_name = 'registration/create_user.html'

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        """
        Form sending function. Note the decorators
        """
        return super(CreateAccountView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        If the form is valid. Attempt to create the user, the profile, and
        link in the RSVP
        """

        # Make the database username the lowercase version of what's been
        #   entered. This will force uniqueness among the names for all
        #   new users. Checking is done in a case-insensitive manner
        username = form.cleaned_data.get('email_address').lower()

        # Finally, we want to make the user object and the profile object
        #   and link them together
        user = User.objects.create_user(
            username,
            form.cleaned_data.get('email_address'),
            form.cleaned_data.get('password1'),
            first_name=form.cleaned_data.get('first_name'),
            last_name=form.cleaned_data.get('last_name'))
        if not user:
            return HttpResponse("Failed to create user", status=400)

        # And create a profile to link to the user, also linking in the RSVP
        #   that we found
        user_profile = Profile(
            user=user,
            address=form.get_address())
        user_profile.save()
        form.rsvp.profile = user_profile
        form.rsvp.save()

        user_cache = authenticate(
            username=username,
            password=form.cleaned_data.get('password1'))
        if user_cache is None:
            return HttpResponse("Failed to log in user", status=400)

        login(self.request, user_cache)
        return HttpResponseRedirect(self.success_url)
