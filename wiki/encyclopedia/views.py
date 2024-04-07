from django.shortcuts import render, redirect
from django.http import HttpResponse,Http404
from django import forms
import markdown2
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
import random
import os

from . import util

"""form creations"""
class Searchform(forms.Form):
    query=forms.CharField(label="Search Wiki")

class EditEntryForm(forms.Form):
    content = forms.CharField(label='Content', widget=forms.Textarea)

class newPageForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    content = forms.CharField(label='Content', widget=forms.Textarea)

def index(request):  
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": Searchform()
    })


"""gives the user the ability to edit the wiki page"""
def Editpage(request, name):
    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            content=form.cleaned_data["content"]
            util.save_entry(name, content)
            return redirect("wikirender", name=name)
    else:
        content= util.get_entry(name)
        form = EditEntryForm(initial={'content': content}) if content else None    
    return render(request, "encyclopedia/EditPage.html", {
        "form": form,
        "entry_name": name
    })


"""creates a new page and opens it with whatever is inserted in the form if it doesn't already 
exists or it returns an error if a page with that name already exists"""
def newPage(request):
    if request.method=="POST":
        form=newPageForm(request.POST)
        if form.is_valid():
            title=form.cleaned_data["title"]
            content=form.cleaned_data["content"]
            if util.get_entry(title):
                messages.error(request, f"An entry with the title '{title}' already exists.")
                return redirect(newPage)      
            util.save_entry(title,content)
            return redirect("wikirender", name=title)
    else:
        form=newPageForm()
    return render(request, "encyclopedia/newPage.html", {
        "form": form
    })


"""searches the page the user wrote in the form from the list of existing pages and opens it or returns an error if it doesn't exist"""
def searchword(request):
    if request.method == "GET":
        form=Searchform(request.GET)
        if form.is_valid():
            query=form.cleaned_data["query"]
            content=util.get_entry(query)              
            if content:
                content=content.split("\n")
                return render(request, "encyclopedia/wikirender.html", {
                    "wikititle": query,
                    "wikicontent": content,
                    "entryexist": True,
                    "form": Searchform()
                })
            else:
                result=[]
                namelist=util.list_entries()
                for name in namelist:
                    if query.lower() in name.lower():
                        result.append(name)
                return render(request, "encyclopedia/searchResult.html",{
                    "query": query,
                    "results": result
                })
    else:
        form=Searchform()
    return render(request, 'encyclopedia/index.html', {'form': form}) 

"""renders the content of the wiki page corresponding to the link"""
def wikirender(request,name):
    page= util.get_entry(name)
    if page:
        html_content= markdown2.markdown(page)
        return render(request, "encyclopedia/wikirender.html",{
            "wikiname": name,
            "wikicontent":html_content,
            "entryexist": True,
            "form": Searchform()
        })
    else:
        return render(request, "encyclopedia/wikirender.html", {
            "wikiname":name,
            "wikicontent":None,
            "entryexist": False,
            "form": Searchform()
        })
    
"""choses a random page to render from the existing pages"""
def random_page(request):
    entries= util.list_entries()
    random_entry= random.choice(entries)
    return redirect("wikirender", name=random_entry)

#wiki deletion form
class DeleteWikiEntryForm(forms.Form):
    entry_name = forms.CharField(label='Wiki Entry Name')

#deletes the wiki entry with the name inserted in the form if it exists, if not it returns an error
def delete_wiki(request):
    if request.method=="POST":
        form = DeleteWikiEntryForm(request.POST)
        if form.is_valid():
            entry_name = form.cleaned_data['entry_name']
            file_path = os.path.join(settings.WIKI_PAGES_DIR, f"{entry_name}.md")
            if not os.path.exists(file_path):
                return render(request, 'encyclopedia/deleteError.html', {
                    'error': "No such file exists"
                    })
            try:
                os.remove(file_path)
                #Redirect to the homepage after deletion
                return redirect('index') 
            except OSError as e:
                return render(request, 'encyclopedia/deleteError.html', {
                    'error': str(e)
                    })
    else:
        form = DeleteWikiEntryForm()
    return render(request, 'encyclopedia/delete_form.html', {
        'form': form
        })

