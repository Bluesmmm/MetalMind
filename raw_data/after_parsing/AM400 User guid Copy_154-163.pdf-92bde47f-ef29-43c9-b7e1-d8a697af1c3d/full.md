# 25.1 Heat soak procedure  

The use of the heated build plate is guided by the choice of materials. It can aid material flow and assist the processing of some materials. Above $7 0 ^ { \circ } \mathsf { C }$ ( $1 5 8 ^ { \circ } F )$ the door remains interlocked and does not allow the main process chamber door to be opened.  

# WARNING: IT IS POSSIBLE TO ACCESS THE CHAMBER VIA THE GLOVE BOX WHILST THE HEATER IS ON. ALWAYS CHECK THE CHAMBER TEMPERATURE VIA THE HMI TOUCH SCREEN BEFORE OPENING THE GLOVE BOX DOOR AND PROCEED WITH CAUTION.  

Login at the delegated user level and select the heater from the main menu on the control interface (Figure 233). Enter the required material temperature (Figure 234). Always refer to the material file supplied with your metal powder for the most accurate temperature to suit your application.  

![](images/3205817783306e44b0fb20ec77115d97155939f74c046e6bdfe1cac7dd02f3bd.jpg)  
Figure 233 Select heater  

![](images/ab853577bf6f8425c84bd88af5ab497b4825c79088a4b986d6767f9c0fea9719.jpg)  
Figure 234 Enter temperature  

# Heater $>$ Set Temperature $>$ Enter the required material temperature  

Always refer to the material file supplied with your metal powder for the most accurate temperature to suit your application. If the material file is not available or you would like further advice contact your local Renishaw office, www.renishaw.com/contact  

Begin the heater soak cycle by selecting the following on the control interface (Figure 235):  

![](images/3d2b62e6e10f76f2ae299dd18d7dd56ae64f8b8eae9b34896aaa5e507923bb98.jpg)  
Figure 235 Press Soak Cycle  

# Heater $>$ Soak Cycle  

The heat soak process lasts for 40 minutes – this is to allow an even temperature throughout the build chamber.  

Caution: Do not attempt to drive the z-axis until the heat soak process is complete. Always allow 30 minutes for the system temperature to stabilise before driving the z-axis if the heat soak process is aborted.  

# 25.2 Heater tuning  

# 25.2.1 Summary  

The AM250/AM400 is fitted with a heated build plate, this will be factory set for optimum performance. If a significantly thicker build plate is used or the Heater May Require Tuning alarm message appears there is an Autotune function which will determine the settings required for the best heater response. (Proportional Band, Integral Constant and Derivative Constant).  

Note: This requires level 2 access with software version 2.39 or greater, and level 3 access with earlier software versions.  

Heater setup must be performed under an inert atmosphere and with the build plate installed, as both will affect the thermal characteristics.  

# 25.2.2 System preparation  

Install a build plate and setup the system, ensure there is no powder in the chamber.  

Set the user oxygen threshold to 1000 parts per million and start the Semi Automatic Chamber Preparation with vacuum.  

Leave the system to prepare.  

# 25.2.3 Automatic tuning  

Select Heater (Figure 236).  

![](images/8108139f562d400a25cea43b36739e9f51e201465c51d4e64e0bfe326924dc53.jpg)  
Figure 236 Select heater  

Adjust the set Set Temperature to $1 0 0 ^ { \circ } \mathsf { C }$ .  

Ensure the Period is 1 second.  

Press On followed by Autotune Start (Figure 237).  

![](images/040f07b3b8a6ff334db31e77bb3c0ef77d8ef43b5ad6ad6e65f1b40c8989bbc5.jpg)  
Figure 237 Set temperature to $1 0 0 ^ { \circ } \mathsf { C }$ , period 1, On, Autotune Start  

The progress can be monitored by pressing Trending button to show the graph (Figure 238) which displays set-point (SP), present value (PV) and $\%$ demand (MV). The auto tune process will take approximately 10 to 20 minutes.  

On completion of the auto tune process record the new Proportional Band, Integral Constant, and Derivative Constant will be saved.  

![](images/46039dd19ca450040d6e05bf333571ea62a6d3f024ba77b0a5770962101064f2.jpg)  
Figure 238 Temperature and demand graph  

Leave for 40 minutes to settle, once stable the demand (MV) should only fluctuate slightly (Figure 239).  

![](images/fba9e9738362bb2533a7e37d8fa8472dd40a16a4367b364a0f63ed9422000622.jpg)  
Figure 239 Stable temperature and demand  

If the heater demand (MV) oscillates and does not quickly settle it may be necessary to repeat the process a 2nd or 3rd time (Figure 240 and Figure 241).  

![](images/e0375269e208bb9df3cbe0210311464d7e152a2c759982534debe20358f4c213.jpg)  
Figure 240 Demand oscillations  

![](images/646fdd32ff1cef9e7cadf94cbd26bc1efece9f0c36c9891b73d365b7f3eb5642.jpg)  
Figure 241 Demand oscillations hitting zero  

# 25.2.4 Testing  

The heater should be permitted to cool before testing, this may take several hours.  

Change the set temperature to $1 7 0 ^ { \circ } \mathsf { C }$ .  

Switch the heater On.  

Open the graph by pressing Trending.  

The duty of the heater should start at $100 \%$ and drop as the temperature reaches target value.   
Temperature should not overshoot the target temperature (Figure 242).  

![](images/f2fe047dca51932fb44ac177f66273aa09f09e5b3c5e7ac9758e39421e51062f.jpg)  
Figure 242 Demand at $100 \%$ as temperature increases  

Demand and temperature should then both stabilise.  

Leave a further 40 minutes to heat soak, the demand and temperature should now both be stable as shown, (Figure 243).  

![](images/ca82adcd52165bad208b2d818fb20cbc918c00ebf09f3a9bf419b58d70455092.jpg)  
Figure 243 Consistent heater duty at $1 7 0 ^ { \circ } \mathsf { C }$  

Press Off on the Elevator Heater page and wait for the system to cool.  

# 26.1 Setting up a file transfer service  

Install a suitable FTP transfer service.  

Note: Renishaw recommend using WinSCP for file transfer. WinSCP is freeware.  

![](images/0db26f4ab003063077523d843ed251e2ac9dc8cb843cf1cfa58d1074fb1cb0cf.jpg)  
Figure 244 WinSCP icon  

Save your Renishaw system location with the following settings (Figure 245):  

File protocol: FTP (File Transfer Protocol)   
Host name: The IP (Internet Protocol) address can be found on the service menu of the AM system (this can be renamed to the assigned system name if required)   
User Name: AM-User   
Password: ampdam250 (case sensitive)  

![](images/7ba4a2fbe1ff979c9ff715538ab6884ba72c2d4198577e47d7f8f0ba49689f1e.jpg)  
Figure 245 Login details  

# 26.2 Sending a file to the system  

Open WinSCP.  

Select your system name from the network addresses and login (Figure 246):  

![](images/62a725052ab18265e72e9fc718c97a4745c4183f052131600fc800e619e36a2c.jpg)  
Figure 246 Select system  

Navigate to the directory where your .mtt file is saved and drag the file into the Builds folder in the right hand column (Figure 247). Accept the prompt to copy.  

![](images/42f056e8c02a949a1ca111ef767cdee10b4d00884ab63e1d247ed43d21c044ff.jpg)  
Figure 247 Drag file into build folder  

# 26.3 Setting up FTP  

If using a standalone computer connected to the system the passive FTP, which is usually set during the system setup, must be reset after a Windows update. Automatic updating of windows should also be switched off. If this is not done there may be communication failures when transferring builds.  

Resetting the File Transfer Protocol  

1. Open Control Panel (Figure 248) then Internet Options (Figure 249).   
2. Select Advanced from the top bar menu.  

![](images/a7968a5aaec6a00820bb7b255e16f40484abf6e174d7a35f22d51f28d8a99293.jpg)  
Figure 248 Control panel  

![](images/6bd77f4811ab1851120d2d5c5ec4f9e535902f99e556daf79bac7d0a414062d8.jpg)  
Figure 249 Internet options  

3. Scroll to Browsing.  

4. Deselect Use passive FTP (for firewall and DSL modem compatibility).  

# Controlling future windows updates  

To prevent Windows from automatically updating, and overwriting the FTP settings, complete the following steps:  

1. Select Control Panel, then Windows update.  

2. Select Change settings (Figure 250).  

![](images/cb0ac6e4340926b53c9dd3754a34f85d27104c62e2379d87d066607c8833a817.jpg)  
Figure 250 Select change settings in windows update  

3. Using the drop down menu, select Let me chose whether to download and install updates. This will prevent Windows from automatically changing the FTP settings (Figure 251).  

![](images/b591fb66fe80cc2c9ee555725329909e4f360887684440e678dd3a0c48a83824.jpg)  
Figure 251 Select Let me choose whether to download and install updates  

4.	 If manual updates are made, it may be necessary to reset the FTP settings again after the update.  

# 26.4 Selecting a file from the list  

Transferring a build onto the system is done via a local network connection from the file preparation PC to the system. Once completed, the build will appear in the Select Build menu (Figure 252).  

![](images/c1b6ee3518027b2c7719b48d628e3f349e4ffeb985aee48771f362ff335c4c90.jpg)  
Figure 252 Select build menu  

Note: Up to ten build files can be stored on the AM250/AM400 system.  