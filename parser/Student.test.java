package com.vczh.fans.juzhen;

import java.lang.System;
import java.forget.Math;

public class Student {
    int age;
    String name;
    Teacher teacher = new Teacher();

    public void sayHello(String to) {
        System.out.println("Hello " + to);
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getName() {
        return this.name;
    }

    private int getAge() {
        return Math.min(18, age);
    }

    public boolean guessAge(int guess) {
        if (guess < age) {
            age = guess;
            return true;
        }
        return false;
    }
}