import adsk.core, adsk.fusion, adsk.cam, traceback

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('SampleScriptButtonId', 
                                                   'Python Sample Button')
        
        # Connect to the command created event.
        sampleCommandCreated = SampleCommandCreatedEventHandler()
        buttonSample.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)
        
        # Execute the command.
        buttonSample.execute()
        
        # Keep the script running.
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class SampleCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        
        # Get the command
        cmd = eventArgs.command

        # Get the CommandInputs collection to create new command inputs.            
        inputs = cmd.commandInputs

        # Create a check box to get if it should be an equilateral triangle or not.
        equilateral = inputs.addBoolValueInput('equilateral', 'Equilateral', 
                                               True, '', False)

        # Create the slider to get the base length, setting the range of the slider to 
        # be 1 to 10 of whatever the current document unit is. 
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)
        minVal = des.unitsManager.convert(1, des.unitsManager.defaultLengthUnits, 'cm' )
        maxVal = des.unitsManager.convert(10, des.unitsManager.defaultLengthUnits, 'cm' )
        baseLength = inputs.addFloatSliderCommandInput('baseLength', 
                                                       'Base Length', 
                                                       des.unitsManager.defaultLengthUnits,
                                                       minVal, maxVal, False)

        # Create the value input to get the height scale. 
        heightScale = inputs.addValueInput('heightScale', 'Height Scale', 
                                           '', adsk.core.ValueInput.createByReal(0.75))

        # Connect to the execute event.
        onExecute = SampleCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)


# Event handler for the execute event.
class SampleCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        # Code to react to the event.
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)        
        
        if des:
            root = des.rootComponent
            sk = root.sketches.add(root.xYConstructionPlane)
            lines = sk.sketchCurves.sketchLines
            l1 = lines.addByTwoPoints(adsk.core.Point3D.create(0,0,0), 
                                      adsk.core.Point3D.create(5,0,0))
            l2 = lines.addByTwoPoints(l1.endSketchPoint,
                                      adsk.core.Point3D.create(2.5,4,0))
            l3 = lines.addByTwoPoints(l2.endSketchPoint, l1.startSketchPoint)

        # Force the termination of the command.
        adsk.terminate()   
 
           
def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Delete the command definition.
        cmdDef = ui.commandDefinitions.itemById('SampleScriptButtonId')
        if cmdDef:
            cmdDef.deleteMe()            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))