## Blitzkrieg: Advanced Browser Sidebar


## Screenshots:

<img src="https://github.com/lovac42/blitzkrieg/blob/master/screenshots/demo.gif?raw=true">  


<img src="https://github.com/lovac42/blitzkrieg/blob/master/screenshots/autoupdate.png?raw=true">  


## Operations:
Drag and drop items.  
Right-Click to show context menu.  
Shift+RClick to show alternative context menu.  


### Search:
Search highlights are cleared on refresh or on exiting the browser.  
The startswith and endswith options only searches full names not the subtree.  


## Performance:
Warning: Performance is questionable with more items. Keep it under 2000 items total. Plus or minus 20% per CPU depending on system speed.

<img src="https://github.com/lovac42/blitzkrieg/blob/master/screenshots/sidebar_item_count.png?raw=true">  


## Night Mode Conflict Resolution:
NM uses a unique method of patching into Anki that causes problem for ALL addons. Just make sure it loads last after all other addons have been loaded by changing it's folder name with a 'z' prefix. z828472. Or change this addon's folder name with an 'a' prefix a536247578. But changing folder names will prevent updates notifications, so it is far better to change nightmode as it screws up all other addons.


## Credits:
Loosely based on Hierarchical Tags, by Patrice Neff:  
https://ankiweb.net/shared/download/1089921461  

