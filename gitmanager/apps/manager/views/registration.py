from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.models import Group
from gitmanager.apps.manager.forms.register_form import RegistrationForm
from gitmanager.apps.manager.forms.forgot_password import ForgotPasswordForm
from gitmanager.apps.manager.forms.reset_password import ResetPasswordForm
from django.contrib import auth
from django.template import RequestContext
from django.contrib.auth.models import User
from gitmanager.apps.manager.models.authentication import PasswordResetTokens
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from gitmanager.config.settings import *
import uuid

def reset_password(request, user_id, token):
    error = False
    success = False
    
    try:
        user_exists = User.objects.get(pk=int(user_id))
        
        try:
            user_reset_token = PasswordResetTokens.objects.get(user_id=user_exists, token=token)
        except ObjectDoesNotExist:
            error = 'The reset token is invalid'
            
    except ObjectDoesNotExist:
        error = 'The user does not exist'
    
    if not error and request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            
            if cd['password1'] != cd['password2']:
                error = 'The passwords do not match'
            else:
                user_exists.set_password(cd['password1'])
                user_exists.save()
                
                success = True
    else:
        form = ResetPasswordForm()
        
    return render_to_response('registration/reset_password.html', {'token': token, 'user_id': user_id, 'form' : form, 'success': success, 'error': error}, context_instance=RequestContext(request))    
    

def forgot_password(request):
    error = False
    success = False
    
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            
            email = cd['email']
            
            try:
                user_exists = User.objects.get(email=email)
                
                token = uuid.uuid4().hex
                
                try:
                    prt = PasswordResetTokens.objects.get(user_id=user_exists)
                    
                    prt.token = token
                except ObjectDoesNotExist:
                    prt = PasswordResetTokens(user_id=user_exists, token=token)
                    
                
                prt.save()
                
                subject = 'GitManager Password Reset'
                message = 'You have requested a password reset. '
                message += 'Please click the link below to reset your password: \n\n'
                message += 'http://127.0.0.1:8000/accounts/reset-password/' + str(user_exists.id) + '/' + token + '/'
                
                send_mail(
                    subject,
                    message,
                    ADMIN_EMAIL,
                    [SENDTO_EMAIL],
                )
                
                success = True
                
            except ObjectDoesNotExist:
                error = 'No user with that email address exists'
            
    else:
        form = ForgotPasswordForm()
        
    return render_to_response('registration/forgot_password.html', {'form' : form, 'success': success, 'error': error}, context_instance=RequestContext(request))    
    
def register(request):
    error = False
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            
            try:
                g = Group.objects.get(name='Registered')
                g.user_set.add(new_user)
            
                new_user = auth.authenticate(username=request.POST['username'], password=request.POST['password1'])
                auth.login(request, new_user)
                return HttpResponseRedirect('/manager/list-repositories')
            
            except ObjectDoesNotExist:
                error = 'Could not create user. Invalid group specified.'
    else:
        form = RegistrationForm()

    return render_to_response('registration/register.html', {'form' : form, 'error': error}, context_instance=RequestContext(request))