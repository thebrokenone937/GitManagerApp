from django import template
import time

register = template.Library()

@register.filter
def uni(value): 
    return unicode(value)

@register.filter
def convert_colors(value):
    
    value = value.replace('<', '&lt;')
    value = value.replace('>', '&gt;')
    value = value.replace('[1m', '<span style="color: #000; font-weight: bold">')
    value = value.replace('[32m', '<span style="color: #009900;"> +')
    value = value.replace('[36m', '<span style="color: #000099;">')
    value = value.replace('[31m', '<span style="color: #ff0000;"> -')
    value = value.replace('[m', '</span>')
    value = value.replace('\n', '<br />') 
    value = value.replace('diff --git', '<br /><hr /><br />diff --git')
    value = value.replace(' @@', ' @@<br /><br />')
     
    return unicode(value)

@register.filter
def format_commit_date(value):
    if value:
        return time.strftime("%a, %d %b %Y %H:%M", time.gmtime(float(value)))
    else:
        return value