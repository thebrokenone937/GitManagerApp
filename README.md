This is a simple project I started to learn more about Django and Git.
It lets you add git repositories & view the last 100 commits. You can click into
the commits & it will show the diff for it. You can then comment on the commit.

It has a login and registration system. There are a few features I haven't added yet
such as adding other users to a repository. I was thinking I could further develop
it into a simple code review tool like Gerrit or ReviewBoard.

I need to add unit tests for this application also.

I need to allow for adding repositories that under ssh.


There are a couple of things you need to do to get this working:

You need to replace the database credentials with your own.

You need to replace the email settings with your own also.

Emails are sent in the forgot password form & when you add a comment to a commit
diff. It's currently configured to take the "from" email address from the ADMIN_EMAIL
variable and the recipient list from the SENDTO_EMAIL variable in settings.py 

You need to replace REPO_BASE_DIR in settings.py with a directory on your machine.
It will use this directory to clone the repositories into.


Other notes:

I followed this article for splitting the models into different files:

http://www.essentialcode.com/2009/01/26/splitting-django-models-into-separate-files/
