from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
import markdown2
from django.urls import reverse
from django.contrib import messages
import random

from . import util

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
    

def random_page(request):
    entries= util.list_entries()
    random_entry= random.choice(entries)
    return redirect("wikirender", name=random_entry)
