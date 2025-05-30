# 27 Starting the build  

Check that all the steps have been completed and all the necessary system checks are complete. In particular pay attention to:  

Powder level via the HMI   
Pressure of gas in the argon bottle   
Regulated argon pressure   
Condition of the chiller, ensuring that fluid levels are close to the upper level marker  

# 27.1 Process checks  

Confirm each of the steps have been completed before starting the build:  

Ensure the system has been cleaned down Login to AM250/AM400 control interface, open door Confirm chamber pressure is reading zero, if not see Section 18.3 – "Checking the pressur sensor" Transfer powder from supplier's container to system powder bottle Load powder Install substrate Assemble/install wiper. Dose powder to check for even distribution Heat soak procedure Install front and rear overflow bottles Install safe change filter assembly OR large safe change filter assembly • Check argon cylinder pressure greater than 25 bar, supply pressure less than 2 bar • Check the valve positions: Safe change filter/large safe change filter – 4 open (V4, V5, F1 and F2) Overflow bottles – 4 open (A1, B1, V2 and V3) Silo filling valve – 1 closed (V1) • Select file and start build  

# 27.2 Initiating the build  

First of all double-check all the valve positions are correct. The system will not operate correctly unless:  

• Safe change filter/large safe change filter – four valves are open (V4, V5, F1 and F2) Small rear overflow bottle – both bottle and pipe valves are open (A1 and V2) • Large front overflow bottle – both bottle and pipe valves are open (B1 and V3) • Silo – top valve is closed – even if a bottle is present (Figure 219) (V1) • Silo – dosing valve is open (Figure 253) (IV1)  

![](images/dab0353bf662c6e5a44e2fae1b5e14825c768b3b057b6b796cb98f68b1dc6418.jpg)  
Figure 253 Silo top valve in closed position (V1)  

The KF valve is open when aligned with the flow direction, and shut when the lever is $9 0 ^ { \circ }$ to the direction of flow (Figure 219).  

Note: The silo dosing valve (IV1) is an exception to the rule and is open when perpendicular to flow (parallel to the ground – shown in inset of Figure 254).  

![](images/481adff412f39fddc339bf5c86f1b294ffcb07e6be18460b10748766f757c095.jpg)  
Figure 254 Open the silo dosing valve (IV1) by pushing away  

From the main menu on the control interface, select Select Build (Figure 255).  

![](images/df7664ccdd9d70f70c2c802f61ddf26e301eebe38a4d77f504165756505a2e70.jpg)  
Figure 255 Main menu  

Select the previously uploaded build name (Figure 256).  

![](images/c1927222cd0b854587301aa3850dc242ded7eaea21235c0e78af4d8235a8cef0.jpg)  
Figure 256 Select build name  

Return to the main menu by pressing the Esc. button at the top left on the HMI. Select Wiper/Elevator Control (Figure 257).  

![](images/6d5da766980f83d04642077b2caa9d86d85e2a4b179c3af9afe797aa06ecbaa9.jpg)  
Figure 257 Wiper control screen  

Select Find Wiper Home, ensuring that the wiper and substrate cannot collide.  

# Wiper/Elevator Control $>$ Find Wiper Home  

Ensure that the wiper installation has been performed correctly.  

Once complete, press Set Datum on the control interface.  

# Wiper/Elevator Control $>$ Set Datum  

Press Esc and select the Auto menu (Figure 258) and press the Play button (Figure 259).  

![](images/d3a7dfbd8db9a2fa145726594a9fd789a44b226334a859e917f0fe542d52eefe.jpg)  
Figure 258 Select auto  

![](images/fbdeb94dd1e8ac3c97bec9c21cccf49e8d94f8d56c239e684b134932d55c117c.jpg)  
Figure 259 Press play  

When prompted, ensure that the safe change filter valves (F1, F2, V4 and V5) are open and confirm this on the interface by pressing Yes (Figure 260).  

![](images/c4b0529726982bb271f662c5b09af64c2d725d880001c52544d02c9c0cff801c.jpg)  
Figure 260 Confirm by pressing Yes  

# 27.3 Stabilising the atmosphere  

At this point the system will start the process of creating the inert atmosphere. This takes between 10 and 15 minutes and throughout the process the HMI touch screen gives status updates.  

Once the preset oxygen atmosphere threshold has been achieved, the system waits two minutes for the atmosphere to stabilise. If the threshold rises above the preset limit, the system will dose additional inert gas to achieve the required level and then wait a further two minutes.  

# 27.4 Maintaining the build  

WARNING: DO NOT REMOVE OR ATTEMPT TO CHANGE THE LARGE SAFE CHANGE FILTERWHILST A BUILD IS RUNNING. DO NOT OPERATE THE LARGE SAFE CHANGE FILTER VALVES(V4, V5, F1 AND F2) WHEN A BUILD IS RUNNING.  

Note: Once the build has started, observe the first few minutes of the build process and check that the gas flow is correct from right to left, the quality of the part is acceptable, the powder is dosing correctly and the laser appears to be functioning correctly.  

Once started, the system will then run automatically. Periodically the system operator will need to add new material and take away unused material that has been collected in the overflows.  

The frequency of these activities is dictated by two factors:  

The cross sectional area of the part The amount of powder that is over-dosed  

# 27.5 Setting the dosing percentage  

Dosing is set via the HMI. Some degree of judgement is required for this value to be set, as it is dependent on the cross section of the part and also the layer thickness dictated by the materials file.  

Typically, a build in $2 5 \mu \mathrm { m }$ (0.001 in) layers requires a dose of around $40 \%$ . Thicker layers require a larger dose. The exact dose percentage depends upon the material being used, the part density on the build plate and part placement on the build plate. Experience of builds will guide you in selecting the correct dose percentage. The operator should aim to have powder in front of the wiper for the whole sweep and a small amount of powder wiped down the overflow. Overdosing will result in extra sieving, under dosing will only partially complete the build.  

To set the dose, login at level 2 and select the Service button (Figure 261).  

Following this, select the User settings button (Figure 262).  

![](images/7ca320bcecc095653f961a092c92f9362dba614d2ea5be2a0596a03515f046bf.jpg)  
Figure 261 Select Service  

![](images/bf86d004938c7aa3c253511ac3822a0035efff34bac2aaf49e50d01b77449558.jpg)  
Figure 262 Select User settings  

This then leads to the page that allows you to configure various settings including material, dosing, wiper speed and maximum oxygen threshold (Figure 263).  

![](images/c24fa3eb14d73b0942adf073a28e5d98d76ab66c21a4957caf0294b54847bd99.jpg)  
Figure 263 User-configurable settings  

It is possible to amend the dosing percentage during the build.  

For rapid powder delivery the dose can be setup to $300 \%$ – three fully open doses per wipe.  

# 27.6 Restarting a build from a specific layer number  

On the auto operation screen Layer No. PV (Present Value) will typically display the layer number. Alternatively divide the build height by the layer thickness (for example $6 \ : \mathrm { m m }$ in $5 0 \mu \mathrm { m }$ layers $= 6 / 0 . 0 5$ $= 1 2 0$ layers).  

If the last layer number is not known, Enter Service Menu (Figure 264).  

![](images/b650c4ac1577ba435f9b486023fb92f27e75f8b47fbcb3680ccc40b039c12a53.jpg)  
Figure 264 Service menu  

Enter run counters menu, check the Last layer number in previous build value (Figure 265).  

![](images/e911ddaa15c33cd1e127a1ebb433dc740cb957b39c7e676755d40f4ac0165271.jpg)  
Figure 265 Run counters  

From the menu select Wiper/Elevator Control enter the required start layer into Layer No. Reset the datum by pressing Set Datum (Figure 266).  

![](images/31b236a0c0eaf1a11582f6e9e9452257a11dc5bb213b618a85a6d21ee2b3c822.jpg)  
Figure 266 Enter layer number and set datum  

In Auto press Play.  

An on screen prompt will appear, confirm the Start at Layer Number figure is correct and press Yes (Figure 267).  

![](images/1008eb97ec18a874addbd6886338b54a255c4f778ab501f48ef74f6db7a35a2a.jpg)  
Figure 267 Check layer number and continue  

Open safe change filter valves (F1, F2, V4 and V5) and proceed as a normal build.  

# 27.7 Suppressing a part  

In the Auto screen press View Parameters and then Slice Preview (Figure 268). Determine the number(s) of the part(s) to be suppressed (Figure 269).  

![](images/87ac8e7fd9489c63af0f0795e6e3ac2785bdf78c8f43753ccb3fc677368c47bc.jpg)  
Figure 268 Slice preview  

![](images/ba7cb07de24c1d9f18e310745d16d463d9fa694cc5a50b0e7d950ec345d68101.jpg)  
Figure 269 Check component numbers  

In the Auto screen press Pause, additional functions will appear, press Suppress part (Figure 270).  

![](images/cb73c2e75eb86194155313a2c84fdd63736d8c2b0376b1ac5678fed33b305164.jpg)  
Figure 270 Suppress parts  

Enter the part number into Suppress part number (Figure 271) follow the on screen prompts to suppress the part.  

![](images/5ba8ed64e388a1e6b1c6b737cb6a2900ff10691b0c30ea5681676714f6ed3f38.jpg)  
Figure 271 Suppress parts  

Repeat if necessary for each part number.  

Press Escape to exit the menu, press Play to re-commence the build (Figure 272).  

# 27.8 Halting a build part way through  

The Emergency Stop button should only be used to stop the build in an emergency. It will instantaneously halt the complete system, which will interfere with the software logic – it will not necessarily be possible to restart the build. The z-axis uses an incremental encoder, with a proximity sensor to provide an accurate home position. Using the Emergency Stop will require the home position of the z-axis to be re-taught.  

Note: In the event of a breakdown or accident press the "Emergency Stop". Following assessment of the situation perform a restart procedure if safe, or call Renishaw AM service for support.  

If a non-emergency shutdown is required, first select Auto, then press Pause, (Figure 272 and Figure 273).  

![](images/4a6e7bbbef445f05352f176b41da1a18c1891cdcaee5c326b4378a8c7b3bb3d4.jpg)  
Figure 272 Select auto  

![](images/d6e2378cf87f6362bcdec377ce92e762c96c81bb9e9f21b4e73f74c082217714.jpg)  
Figure 273 Press pause  

# 28.1 Closing the filter valves  

At the end of the process, confirm the build completion when prompted on the AM control interface (Figure 274).  

![](images/f9f9ea1799ea62cea285cf1fcc99c1013c1bedd2ccd12dc7c0c6e5900ce660ca.jpg)  
Figure 274 Build complete prompt in the control interface  

You will then be prompted to close the safe change filter/large safe change filter valves, (V4, V5, F1 and F2) (Figure 275).  

![](images/5fa121fdd8a8445554d13691287a9fcea8224b359cbaf30966e6b05f1b4006ee.jpg)  
Figure 275 Isolate safe change filter  

# WARNING: THE FILTER WETTING (INERTING) PROCEDURE MUST BE FOLLOWED FOR ALL POWDER TYPES AND AFTER EVERY BUILD, SEE SECTION 22.  

To close the four valves (V4, V5, F1 and F2), open the side door on the system to locate the safe change filter/large safe change filter and turn the levers so that they are at $9 0 ^ { \circ }$ to the direction of flow, (Figure 276).  

![](images/21ee1bc97b35d4d6227eb32b5009bbdd7bd938ef46f68f489a738a121e286012.jpg)  
Figure 276 Close safe change filter/large safe change filter upper and lower valves, (V4, V5, F1 and F2)  

Confirm the filter valves (V4, V5, F1 and F2) have been closed (Figure 276) by selecting the following in the AM control interface.  

# $>$ CONFIRM  

The filter valves (V4, V5, F1 and F2) must remain closed until it is ready to be wet inerted. See Section 22 – "Safe change filter and large safe change filter", for details of the inerting and filter replacement process.  

WARNING: THE SAFE CHANGE FILTER/LARGE SAFE CHANGE FILTER MUST BE REPLACED AFTER EVERY BUILD. SEE SECTION 22 "SAFE CHANGE FILTER AND LARGE SAFE CHANGE FILTER" FOR DETAILS.  

# 28.2 Cool down  

Wait for the heater temperature PV (Present Value) to reach room temperature before opening the door (Figure 277 and Figure 278).  

![](images/16545f61eea0cace5edf6022a6e6f548159e42a17315d872b65c5e740ade98b8.jpg)  
Figure 277 Allow PV to drop to $< 4 0 ^ { \circ } \mathsf { C }$  

![](images/30009f1577d1e36b7e72657950150db62d28b152e2a7e14d343cf744e31228b4.jpg)  
Figure 278 PV at $2 6 ^ { \circ } \mathsf { C }$  