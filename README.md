# LEDGestureControl

A system using MediaPipe and OpenCV that adjusts an LED's brightness based on hand gestures. By measuring the distance between the thumb and index finger, the PWM signal sent to an Arduino Nano is controlled, which in turn adjusts the LED's brightness.

Here’s how it works:  
🔹MediaPipe detects the positions of the thumb and index finger in real-time.  
🔹OpenCV calculates the distance between the two fingers.  
🔹The distance is mapped to a range, controlling the PWM signal.  
🔹The PWM signal is then sent to an Arduino Nano, adjusting the LED's brightness accordingly.  
🔹To ensure smooth transitions, Exponential Moving Average (EMA) filtering is applied to avoid abrupt changes.  

This simple interaction shows how IoT devices can be controlled via intuitive gestures, bridging the physical world with digital control!
