# Character-UI
Blender UI for you rigs

# How to 
# Naming

Set the name in the char_info, this name represents name of the master Collection and name of the rig and name of the body object(it also has to have Body suffix), it's case sensitive

For example:
```
char_info = {
    "name": "Ellie"
}
```
- **collection name:** Ellie
- **rig name:** Ellie
- **body name:** Ellie Body
- **outfit collection name:** Ellie Outfits
- **hair collection name:** Ellie Hair

Next step is to add a custom property **nextrrig_properties** to the rig

# Outfits
Outfits are located in a collection called after the character with Outfits suffix

For example:

    Ellie
        - Ellie Outfits
            - Ellie Patrol
            - Ellie Seattle

Outfits will be changed by a select constaining all of the outfit names. You don't have to include the character's name.

The select is going to contain these values:
    
    Ellie Patrol
    Ellie Seattle

# Rig layers
To use named rig layers you have to add custom prop to the armature. Otherwise it's going to genereate 32 buttons for each layer.

**Upcoming feature:** grouping layers, like Left Hand, Right Hand one the same row

To add the custom property:

1. Select armature 
1. click Object Data Properties (the one with the stickman icon) 
1. scroll down to Custom Properties sub menu 
1. click Add 
1. name the prop 'rig_layers'
1. insert value similiar to this: [Face,False,Arms]

This pattern results in a creation of two buttons. Keyword False skips one layer.

Layers are from 0 - 31, first row is 0 - 15.
Those two buttons are going to be toggling only the first (0) and the third (2) layer

# Hairdos
If your model has different hairdos you can create a collection called after the character with a Hair suffix

This collection can either have individual objects or collections as children or both.

Name of the object or collection is going to be used in the hairdos select

    Ellie Hair
        - Ellie Patrol hair (object)
        - Ellie Seattle hair (collection)
            - Bangs (object)
            - Pony tail (object)
            
This collection structure is going to result in a select containing these values:
    
    Ellie Patrol hair
    Ellie Seattle hair

Hair can also be parented to a outfit. If you change outfit from *Patrol* to *Seattle* and the lock button is not enabled it's going to also change the hairdo.

This is simply done by checking if the hair has an outfit collection's name in it's name. But if your hairdo isn't named after the outfit this feature is available after adding custom property to the hair object(currently not possible for hairdos made of multiple objects).

1. Select the hair object
1. Click the object properties button (the one with the square)
1. Scroll down to Custom Properties submenu
1. Click add
1. set name as **outfit**
1. set value as the name of the outfit's collection

# Custom material value

This is usefull when you want to for example add a SSS slider to the UI without using drivers.

In the Shader editor add a Value node and set it's name using this pattern:

name_of_the_character[panel_name,name_of_the_element,data_type,min,max,condition,condition_value]

This looks very complicated but once you understand it, it becomes very easy to use.

There are two panels which can have these custom attributes
- OutiftsPanel
- BodyPanel

The firts part of the name is the name of the Character
    
    Ellie[...]

Text in the brackets are settings for the UI element

### panel_name

this is going to be either *OutfitsPanel* or *BodyPanel*

    Ellie[OutfitsPanel,...]
### name_of_the_element

this is going to be tha name visible in the UI, can contain spaces

    Ellie[OutfitsPanel,SSS,...]

### data_type

- i - integer values -> 1, 2, 3, ...
- f - float values -> 1.0, 1.1, 1.2, ...
- t - on/off values
- c - color, **Not supported yet** 

        Ellie[OutfitsPanel,SSS,f,...]

### max & min

Only works for **i** data_type

    Ellie[OutfitsPanel,SSS,0,0,5,...]

### condition & condition_value

Supper WIP and only works **i** data_type and for outfits

In theory these two values control when the UI element is visible, now it supports only outfits because it was needed.

    Ellie[OutfitsPanel,SSS,0,5,Outfits,Ellie Patrol]

So this UI representing the value node is going to be visible only when current selected outfit is *Ellie Patrol*


#### Possible names of custom values


**For SSS slider:**
    
    Ellie[OutfitsPanel,SSS,f]

**For switching different skin variations***

this slider is going to be visible only when Patrol outfit is active
 
    Ellie[OutfitsPanel,Patrol skin variations,0,5,Outfits,Ellie Patrol]