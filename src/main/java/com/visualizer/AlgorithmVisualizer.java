package com.visualizer;

import javax.swing.*;
import java.awt.*;
import java.util.*;
import java.util.List;
import java.util.Queue;

public class AlgorithmVisualizer extends JFrame {
    private GraphPanel graphPanel;
    private JButton bfsButton;
    private JButton dfsButton;
    private JButton undoButton;
    private JButton resetButton;
    private JButton clearButton;
    private JLabel statusLabel;
    private StringBuilder pathBuilder;

    public AlgorithmVisualizer() {
        setTitle("Algorithm Visualizer");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        graphPanel = new GraphPanel();
        add(graphPanel, BorderLayout.CENTER);

        JPanel bottomPanel = new JPanel();
        bottomPanel.setLayout(new BorderLayout());

        JPanel controlPanel = new JPanel();
        bfsButton = new JButton("Run BFS");
        dfsButton = new JButton("Run DFS");
        resetButton = new JButton("Reset");
        clearButton = new JButton("Clear");
        undoButton = new JButton("Undo");

        controlPanel.add(bfsButton);
        controlPanel.add(dfsButton);
        controlPanel.add(undoButton);
        controlPanel.add(resetButton);
        controlPanel.add(clearButton);

        statusLabel = new JLabel("Traversal Path: ");
        statusLabel.setHorizontalAlignment(SwingConstants.CENTER);
        statusLabel.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));

        bottomPanel.add(statusLabel, BorderLayout.NORTH);
        bottomPanel.add(controlPanel, BorderLayout.SOUTH);

        add(bottomPanel, BorderLayout.SOUTH);

        bfsButton.addActionListener(e -> runBFS());
        dfsButton.addActionListener(e -> runDFS());
        undoButton.addActionListener(e -> graphPanel.undo());
        resetButton.addActionListener(e -> {
            graphPanel.reset();
            statusLabel.setText("Traversal Path: ");
        });
        clearButton.addActionListener(e -> {
            graphPanel.clear();
            statusLabel.setText("Traversal Path: ");
        });
    }

    private void runBFS() {
        if (graphPanel.getNodes().isEmpty()) return;
        
        // Start from the first node or a selected one
        Node startNode = graphPanel.getNodes().get(0); 
        
        new Thread(() -> {
            graphPanel.reset();
            pathBuilder = new StringBuilder();
            SwingUtilities.invokeLater(() -> statusLabel.setText("Running BFS..."));
            bfs(startNode);
            SwingUtilities.invokeLater(() -> statusLabel.setText("Traversal Path: " + pathBuilder.toString()));
        }).start();
    }

    private void bfs(Node start) {
        Queue<Node> queue = new LinkedList<>();
        start.setVisited(true);
        queue.add(start);
        start.setColor(Color.GREEN); // Start node
        graphPanel.repaint();

        appendPath(start);

        while (!queue.isEmpty()) {
            Node current = queue.poll();
            
            // Visualize processing
            if (current != start) {
                current.setColor(Color.ORANGE); // Processing
                graphPanel.repaint();
            }

            try { Thread.sleep(500); } catch (InterruptedException e) {}

            for (Edge edge : graphPanel.getEdges()) {
                Node neighbor = null;
                if (edge.getSource() == current) {
                    neighbor = edge.getDestination();
                } else if (edge.getDestination() == current) {
                    neighbor = edge.getSource();
                }

                if (neighbor != null && !neighbor.isVisited()) {
                    neighbor.setVisited(true);
                    neighbor.setColor(Color.CYAN); // Visited/Enqueued
                    appendPath(neighbor);
                    queue.add(neighbor);
                    graphPanel.repaint();
                    try { Thread.sleep(300); } catch (InterruptedException e) {}
                }
            }
            
            current.setColor(Color.BLUE); // Processed
            graphPanel.repaint();
        }
    }

    private void runDFS() {
        if (graphPanel.getNodes().isEmpty()) return;
        
        Node startNode = graphPanel.getNodes().get(0);
        
        new Thread(() -> {
            graphPanel.reset();
            pathBuilder = new StringBuilder();
            SwingUtilities.invokeLater(() -> statusLabel.setText("Running DFS..."));
            dfs(startNode);
            SwingUtilities.invokeLater(() -> statusLabel.setText("Traversal Path: " + pathBuilder.toString()));
        }).start();
    }

    private void dfs(Node current) {
        current.setVisited(true);
        current.setColor(Color.ORANGE); // Processing
        appendPath(current);
        graphPanel.repaint();
        
        try { Thread.sleep(500); } catch (InterruptedException e) {}

        for (Edge edge : graphPanel.getEdges()) {
            Node neighbor = null;
            if (edge.getSource() == current) {
                neighbor = edge.getDestination();
            } else if (edge.getDestination() == current) {
                neighbor = edge.getSource();
            }

            if (neighbor != null && !neighbor.isVisited()) {
                dfs(neighbor);
            }
        }
        
        current.setColor(Color.BLUE); // Processed
        graphPanel.repaint();
    }

    private void appendPath(Node node) {
        if (pathBuilder.length() > 0) {
            pathBuilder.append("-");
        }
        pathBuilder.append(node.getId());
        SwingUtilities.invokeLater(() -> statusLabel.setText("Traversal Path: " + pathBuilder.toString()));
    }

    public static void main(String[] args) {
        System.out.println("Starting Application...");
        SwingUtilities.invokeLater(() -> {
            try {
                System.out.println("Initializing UI...");
                new AlgorithmVisualizer().setVisible(true);
                System.out.println("UI Visible");
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
        
        // Keep main thread alive to ensure process doesn't exit prematurely in this environment
        try {
            Thread.sleep(60000); // Keep alive for 60 seconds
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
