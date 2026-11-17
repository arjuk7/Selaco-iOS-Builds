#pragma once
#include <mutex>
#include <vector>
#include <cmath>
#include <algorithm>
struct SelacoMenuTap { double x,y; };
struct SelacoTouchState {
 std::mutex mutex;
 bool keys[512]{}; bool pressed[512]{}; std::vector<int> pulses; std::vector<SelacoMenuTap> menuTaps;
 double x=0,y=0,forward=0,side=0; bool menu=true;
 void clear(){for(auto &k:keys)k=false;for(auto &k:pressed)k=false;pulses.clear();menuTaps.clear();x=y=forward=side=0;}
};
extern SelacoTouchState selacoTouch;
void SelacoTouchKey(int key,bool down);
void SelacoTouchPulse(int key);
void SelacoTouchMenuTap(double normalizedX,double normalizedY);
void SelacoTouchLook(double x,double y);
void SelacoTouchMove(double forward,double side);
void SelacoTouchReset();
bool SelacoTouchMenu();
void SelacoTouchDrain();
void SelacoTouchAxes(float *axes);
#ifdef __OBJC__
#import <UIKit/UIKit.h>
UIView *SelacoCreateTouchView(UIViewController *controller);
#endif
