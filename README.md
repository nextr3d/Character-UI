# Character-UI
Blender UI for you rigs

# How to 

Clone or download the repository. Open Blender and navigate to the text editor. Click on the *Text* tab and than *Open*. Navigate to the folder with 
**nextrrig_ui.py** and open it. 

# Naming

Every feature is demonstrated in the template.blend file. If you are unsure how to do something try to compare it with the file.

There are a few steps you need to do so the script can work properly.

Open the text edito again with the script and on line 6 is a variable called **character_name**, replace *Suzanne* with the name of your character.

Contents of the variable is also the exact name of the master Collection housing the rig which has also the same name and all of the objects belonging to the character.

The rig should be direct child of the master collection but it doesn't matter it just for your ease of acces to it.

The master Collection can be divided to the more collections recognized by the script. Keep the upper case characters!

 - *Suzanne* Outfits
 - *Suzanne* Body
 - *Suzanne* Hair

## The Outfits collection

This collection is should only contain more collections and each one is one outfit.
The name doesn't matter but it's going to be show in the UI. 
- *Suzanne* Outfit 1
- *Suzanne* Outfit 2

The script will show 2 outfits. 
Each outfit can contain as many objects as you want, their name is going to be used as the label for the button in the UI.
You can nest objects and the parent is going to toggle it's children.

For example if you have a belt and on the belt there are some items, like gun in a holster. You can parent the holster to the belt, and gun to the holster. The UI is going to recognize it and if you hide the belt it's going to hide the holster and since the gun is a child if the holster it's also going to get hidden. 

Outfits can also be combined. If you click on the lock button next to item it's not going to be hidden when you select a different outfit. You don't have to do anything for it to work.

#### Auto masking

Sometimes your weight painting is not perfect on the body and on the clothing and you need to mask certain parts to remove clipping. The UI will automatically enable/disable the mask modifier if you toggle the clothing piece or change outfit.

For it to work add a modifier and name it so it contains the exact name of the object and the word **mask**

For example like this:

Possible names|
---|
Hatmask
HatMask
Hat mask
Hat Mask

#### Auto shape keys

This fature works like the *auto masking* but with shape keys.

You just need to add a shape key on the body object containing the name and the word **shape**

Possible names|
---|
Hatshape
HatShape
Hat shape
Hat Shape

    
#### [WIP] Exposing properties to the UI

> This feature is stable but lack user friendly setup

You can expose modifiers to the UI but this feature is hard to set up because there is no user friendly or automated way.
You will have to open the Console and use this command:

```python
bpy.data.objects['Hat'].data['settings'] = {'modifiers':['Subdivision']}
```

This command sets a custom **settings** property to the **Hat** object and sets to contain this value *{'modifiers':['Subdivision']}*

The key *modifiers* is there so the script know what type of setting it is(in the future I'd like to add more types) and in the [] are the names of the modifiers on the object. If it's not visible in the UI it means that the name is not exact. If sucessfully added you'll be able to toggle teh visibility of the modifier from the UI. (You can check it in the template file)

## The Body Collection

This collection should contain all of the meshes which are part of the body, eyes, teeth, horns,...

It also has to contain the bodu object and it's name has to be 

##### *Suzanne* Body

## The Hair collection

This collection contains all of the hairdos. It special in a way that it can contain both objects and collections but they are threated the same. It's because complicated hairdos can be made out of multiple different objects.

If your hair object or collection contains in it's name name of an outfit and you don't have the lock icon enabled it is going to change the hair to match the outfit. Not all hairdos have to have outfit and vice versa.

Check the template file if you are not sure how any of this works.


# [WIP] Attributes


> This feature is stable but lack user friendly setup

> This feature has not been tested

The UI supports custom attributes to be added to the UI which let's you control things from one place.

It supports syncing properties.


# TODO

- [ ] Add UI for setting up settings
- [ ] Add UI for setting up attributes
- [ ] Test attributes 