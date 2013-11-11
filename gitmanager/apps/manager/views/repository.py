# -*- coding: utf-8 -*-
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.models import Group
from django.contrib import auth
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from git import Repo
from gitmanager.apps.manager.forms.add_repository import AddRepositoryForm
from gitmanager.apps.manager.forms.add_comment import AddCommentForm
from gitmanager.apps.manager.models.repositories import *
from gitmanager.apps.manager.models.comments import *
from gitmanager.config.settings import *
from datetime import datetime 
import os
import uuid
import time

def check_user_repository_access(request, repository_id):
    error = False
    
    try:
        currentUser = User.objects.get(pk=request.user.id)
    except ObjectDoesNotExist:
        error = 'Could not retrieve user'
      
    try:    
        repo = Repositories.objects.get(pk=repository_id)
    except ObjectDoesNotExist:
        error = 'Repository does not exist'
        
    if not repo:
        error = 'No repository with this id'
    else:
        try:
            repoUser = RepositoryUsers.objects.get(user_id=currentUser, repository_id=repo)
        except ObjectDoesNotExist:
            error = 'You do not have permission to view this repository'
    
    return error

@login_required
def edit_comment(request, repository_id, commit_hash, comment_id):
    error = False
    success = False
    form = False
    #existing_comment = False
    
    try:
        existing_comment = Comments.objects.get(pk=int(comment_id))
      
        if request.user.id != existing_comment.user_id.id:
            error = 'This comment does not belong to you'
    
    except ObjectDoesNotExist:
        error = 'The comment does not exist'
        
    error = check_user_repository_access(request, repository_id)
    
    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            if not error:
                existing_comment.comment = request.POST['comment']
                
                existing_comment.save()
                
                success = True    
    else:
        if not error:
            form = AddCommentForm({'comment':existing_comment.comment})
        
    return render(request, 'repository/edit_comment.html', {'success': success, 'form': form, 'error': error, 'commit_hash': commit_hash, 'repository_id': repository_id, 'comment_id': comment_id})


@login_required
def add_comment(request, repository_id, commit_hash):
    error = False
    success = False
    
    error = check_user_repository_access(request, repository_id)
    
    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            try:
                u = User.objects.get(pk=request.user.id) 
            except ObjectDoesNotExist:
                error = 'Could not retrieve logged in user'
                    
            if not error:               
                cd = form.cleaned_data
                
                comment = Comments(comment=cd['comment'], user_id=u, commit_hash=commit_hash, created=datetime.now(), is_del=False)
                comment.save()
                
                repo = False
                
                try:
                    repo = Repositories.objects.get(pk=repository_id)
                except ObjectDoesNotExist:
                    error = 'The repository does not exist'
                    
                if repo:    
                    repository = Repo(repo.repo_url)
                   
                    git = repository.git
                    
                    #don't accept input from the url when sending a mail
                    hash = git.show(commit_hash, '--format="%H"')
                    hash_parts = hash.split('\n')
                    hash = hash_parts[0]
                    
                    committer_email = git.show(commit_hash, '--format="%ce"')
                    committer_email_parts = committer_email.split('\n')
                    committer_email = committer_email_parts[0]
                    
                    subject = request.user.username + ' has  commented on your commit: ' + hash
                    
                    message = 'Comment submitted by ' + request.user.username 
                    message += ' <' + request.user.email + '> :'
                    message += '\n\n'
                    message += 'Sent to ' + committer_email + '\n\n'
                    message += cd['comment']
                    
                    send_mail(
                        subject,
                        message,
                        ADMIN_EMAIL,
                        [SENDTO_EMAIL],
                    )
                    
                    success = True    
    else:
        form = AddCommentForm()
        
    return render(request, 'repository/add_comment.html', {'success': success, 'form': form, 'error': error, 'commit_hash': commit_hash, 'repository_id': repository_id})

@login_required
def list_comments(request, repository_id, commit_hash):
    comments = False
    
    error = check_user_repository_access(request, repository_id)
    
    if not error:
        try:
            comments = Comments.objects.filter(commit_hash=commit_hash).order_by('created')
        except ObjectDoesNotExist:
            error = 'No comments with this commit hash'
                
    return render(request, 'repository/list_comments.html', {'comments': comments, 'error': error, 'commit_hash': commit_hash, 'repository_id': repository_id})

        
@login_required
def show_diff(request, repository_id, commit_hash):
    error = False
    diff = False
    commit_info = False
    repo = False
    comments = {}
    
    error = check_user_repository_access(request, repository_id)
    
    if not error:
        try:
            repo = Repositories.objects.get(pk=repository_id)
        except ObjectDoesNotExist:
            error = 'The repository does not exist'
            
        if repo:    
            repository = Repo(repo.repo_url)
            
            git = repository.git
            
            diff = git.diff(commit_hash+'^!', '--color-words')
            
            commit_info = repository.commit(commit_hash)
            
            try:
                comments = Comments.objects.filter(commit_hash=commit_hash).order_by('created')
            except ObjectDoesNotExist:
                error = 'No comments for this commit'    
        
    return render(request, 'repository/show_diff.html', {'comments': comments, 'error': error, 'commit_hash': commit_hash, 'commit_info': commit_info, 'repository_id': repository_id, 'diff': diff})

@login_required
def list_commits(request, repository_id, branch):
    error = False
    repo = False
    commits = {}
    branches = []
    
    if not branch:
        branch = 'master'
    
    error = check_user_repository_access(request, repository_id)
    
    if not error:
        try:
            repo = Repositories.objects.get(pk=repository_id)
        except ObjectDoesNotExist:
            error = 'The repository does not exist'    
    
        if repo:
            if not os.path.exists(repo.repo_url):
                error = 'The repo directory for this repository does not exist'
            else:
                repository = Repo(repo.repo_url)
                   
                git = repository.git
                
                repository.remotes.origin.pull()
                    
                commits = repository.iter_commits('origin/' + branch, max_count=100)
                
                branches = git.branch(r=True)
                
                branches = branches.replace('  origin/', '')
                
                branches = branches.split('\n')
                
                branches.pop(0)
            
    return render(request, 'repository/list_commits.html', {'branches': branches, 'error': error, 'repository_id': repository_id, 'commits': commits})

@login_required
def list_repositories(request):
    error = False
    repos = False
    repositories = {}
    
    try:
        currentUser = User.objects.get(pk=request.user.id)
    except ObjectDoesNotExist:
        error = 'Could not retrieve logged in user'
    
    try:    
        repos = RepositoryUsers.objects.select_related().filter(user_id=currentUser)
    except ObjectDoesNotExist:
        error = 'Could not retrieve repository users'
        
    return render(request, 'repository/list_repositories.html', {'error': error, 'repositories': repos})

@login_required
def create_repository(request):
    
    error = False
    success = False
    commitData = {}
    
    if request.method == 'POST': 
        form = AddRepositoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            git_url = form.cleaned_data['git_url']
            
            name_check = Repositories.objects.filter(name=name)
            git_url_check = Repositories.objects.filter(git_url=git_url)
            
            if name_check:
                error = 'A repository with this name already exists'
                
            if git_url_check:
                error = 'This git repository already exists in the system'
            
            if not error:
                
                dirname = "".join(x for x in name if x.isalnum())
                
                
                repo_url = REPO_BASE_DIR + dirname
                
                repo_url += "" + time.strftime("%Y%m%d%H%M%S")
                
                #d = os.path.dirname(repo_url)
                if not os.path.exists(repo_url):
                    os.makedirs(repo_url)
                    
                    try:
                        repos = Repo.clone_from(git_url, repo_url)
                    except GitCommandError:
                        error = 'Could not clone repository'
                else:
                    error = 'The clone directory already exists: ' + repo_url
                
                
                
                #repos = Repo(repo_url) #Repo.clone_from(git_url, repo_url)
                
                try:
                    u = User.objects.get(pk=request.user.id) 
                except ObjectDoesNotExist:
                    error = 'Could not retrieve logged in user'
                    
                if not error and repos:
                    r1 = Repositories(name=name, user_id=u, git_url=git_url, repo_url=repo_url, created=datetime.now(), is_del=False)
                    r1.save()
                    
                    ru1 = RepositoryUsers(user_id=u, repository_id=r1)
                    ru1.save()
                    
                    #git = repos.git
                    
                    #commits = list(repos.iter_commits('master', max_count=10))
                    
                    #commitData = {}
                    
                    #for index, commit in enumerate(commits):
                        #if index < (len(commits)-1):
                            #diff = git.diff(commits[index+1].hexsha, commit.hexsha)
                        #else:
                            #diff = False

                        #commitData[index] = commit, diff
                        
                    success = True
                else:
                    if not error: error = 'Could not create repository'
            
    else:
        form = AddRepositoryForm()

    return render(request, 'repository/create_repository.html', {'form': form, 'success': success, 'error': error, 'commits': commitData})
