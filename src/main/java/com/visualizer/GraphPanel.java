package com.visualizer;

import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import java.util.Stack;

public class GraphPanel extends JPanel {
    private List<Node> nodes;
    private List<Edge> edges;
    private int nodeRadius = 20;
    private Stack<Object> history;
    private Node selectedNode;

    public GraphPanel() {
        nodes = new ArrayList<>();
        edges = new ArrayList<>();
        history = new Stack<>();
        setBackground(new Color(240, 240, 240));
        
        // Add mouse listener to add nodes on click or create edges
        addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                if (e.getButton() == MouseEvent.BUTTON1) { 
                    // Check if clicked ON a node
                    Node clickedNode = getNodeAt(e.getX(), e.getY());
                    
                    if (clickedNode != null) {
                        if (selectedNode == null) {
                            selectedNode = clickedNode;
                            selectedNode.setColor(Color.YELLOW); // Highlight selected
                            repaint();
                        } else {
                            if (selectedNode != clickedNode) {
                                addEdge(selectedNode, clickedNode);
                            }
                            selectedNode.setColor(Color.WHITE); // Deselect
                            selectedNode = null;
                            repaint();
                        }
                    } else {
                        // Add new node if clicked on empty space
                        addNode(e.getX(), e.getY());
                    }
                } else if (e.getButton() == MouseEvent.BUTTON3) {
                     // Right click could be used to deselect or something else
                     if (selectedNode != null) {
                         selectedNode.setColor(Color.WHITE);
                         selectedNode = null;
                         repaint();
                     }
                }
            }
        });
    }

    private Node getNodeAt(int x, int y) {
        for (Node n : nodes) {
            double dist = Math.sqrt(Math.pow(x - n.getX(), 2) + Math.pow(y - n.getY(), 2));
            if (dist <= nodeRadius) {
                return n;
            }
        }
        return null;
    }

    public void addNode(int x, int y) {
        String id = String.valueOf(nodes.size());
        Node newNode = new Node(id, x, y);
        nodes.add(newNode);
        history.push(newNode);
        repaint();
    }

    public void addEdge(Node source, Node dest) {
        // Prevent duplicate edges
        for (Edge e : edges) {
            if ((e.getSource() == source && e.getDestination() == dest) || 
                (e.getSource() == dest && e.getDestination() == source)) {
                return;
            }
        }
        Edge newEdge = new Edge(source, dest);
        edges.add(newEdge);
        history.push(newEdge);
        repaint();
    }
    
    public void undo() {
        if (!history.isEmpty()) {
            Object lastAction = history.pop();
            if (lastAction instanceof Node) {
                nodes.remove(lastAction);
                // Also remove any edges connected to this node (though strictly LIFO would prevent this, 
                // just to be safe if we change logic later)
                edges.removeIf(e -> e.getSource() == lastAction || e.getDestination() == lastAction);
                if (selectedNode == lastAction) {
                    selectedNode = null;
                }
            } else if (lastAction instanceof Edge) {
                edges.remove(lastAction);
            }
            repaint();
        }
    }

    public List<Node> getNodes() { return nodes; }
    public List<Edge> getEdges() { return edges; }

    public void reset() {
        for (Node n : nodes) {
            n.setColor(Color.WHITE);
            n.setVisited(false);
        }
        if (selectedNode != null) {
            selectedNode.setColor(Color.WHITE);
            selectedNode = null;
        }
        repaint();
    }

    public void clear() {
        nodes.clear();
        edges.clear();
        history.clear();
        selectedNode = null;
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Draw edges
        g2.setColor(Color.BLACK);
        g2.setStroke(new BasicStroke(2));
        for (Edge edge : edges) {
            g2.drawLine(edge.getSource().getX(), edge.getSource().getY(), 
                        edge.getDestination().getX(), edge.getDestination().getY());
        }

        // Draw nodes
        for (Node node : nodes) {
            g2.setColor(node.getColor());
            g2.fillOval(node.getX() - nodeRadius, node.getY() - nodeRadius, nodeRadius * 2, nodeRadius * 2);
            g2.setColor(Color.BLACK);
            g2.drawOval(node.getX() - nodeRadius, node.getY() - nodeRadius, nodeRadius * 2, nodeRadius * 2);
            
            // Draw ID centered
            g2.setColor(Color.BLACK);
            FontMetrics fm = g2.getFontMetrics();
            int stringWidth = fm.stringWidth(node.getId());
            int stringHeight = fm.getAscent();
            g2.drawString(node.getId(), node.getX() - stringWidth / 2, node.getY() + stringHeight / 4);
        }
    }
}
