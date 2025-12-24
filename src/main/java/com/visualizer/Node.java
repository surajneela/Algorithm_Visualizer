package com.visualizer;

import java.awt.Color;

public class Node {
    private int x;
    private int y;
    private String id;
    private Color color;
    private boolean visited;

    public Node(String id, int x, int y) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.color = Color.WHITE;
        this.visited = false;
    }

    public int getX() { return x; }
    public int getY() { return y; }
    public String getId() { return id; }
    public Color getColor() { return color; }
    public void setColor(Color color) { this.color = color; }
    public boolean isVisited() { return visited; }
    public void setVisited(boolean visited) { this.visited = visited; }
}
