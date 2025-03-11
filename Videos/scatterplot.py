from manim import *
import pandas as pd
import os
import polars as pl
import random

class ScatterPlotAnimatedScene(Scene):
    def construct(self):
        df = pl.read_parquet('merged_df.parquet')
        df = df[['adjusted_price_100ml', 'Duft.rating']].to_pandas()
        df = df[df['adjusted_price_100ml'] < 300]

        y_min = 3
        y_max = 11
        y_stepsize = 1

        x_max = 300
        x_min = 0 
        x_stepsize = 50

        # Create Axes with labels
        ax = Axes(
            x_range=[x_min, x_max, x_stepsize], 
            y_range=[y_min, y_max, y_stepsize], 
            axis_config={"color": WHITE}
        )

        x_label = Tex(r"Adjusted Price per 100ml (€)", font_size=28).next_to(ax, DOWN, buff=0.5)
        y_label = Tex(r"Scent Rating", font_size=28).next_to(ax.y_axis.get_end(), UP, buff=0.3)  
        title = Tex(r"Perfume Price vs. Rating", font_size=36).to_edge(UP)

        # Add tick labels
        # x_labels = VGroup(*[
        #     Tex(str(i), font_size=24).next_to(ax.c2p(i, 0), DOWN, buff=0.2)
        #     for i in range(x_min, x_max, x_stepsize)
        # ])
        # x_labels = VGroup(*[
        #     Tex(str(i), font_size=24).next_to(ax.c2p(i, 0), DOWN, buff=0.2)
        #     for i in range(x_min, x_max + x_stepsize, x_stepsize)  # Include `x_max`
        # ])
        x_labels = VGroup(*[
            Tex(str(i), font_size=24).next_to(ax.c2p(i, 0), DOWN, buff=0.1)  # Adjust buffer
            for i in range(x_min, x_max + x_stepsize, x_stepsize)
        ])
        y_labels = VGroup(*[
            Tex(str(i), font_size=24).next_to(ax.c2p(0, i), LEFT, buff=0.2)
            for i in range(y_min, y_max, y_stepsize)
        ])

        # Animate the axes
        self.play(Write(ax), Write(x_label), Write(y_label), Write(title))
        self.play(LaggedStart(*[Write(label) for label in x_labels + y_labels], lag_ratio=0.01))

        # Convert points into dots
        dots = [Dot(ax.c2p(x, y), color=BLUE, radius=0.02) for x, y in df.sample(n=1500).values]  # Use only 500 points for animation
        dots = [Dot(ax.c2p(x, y), color=BLUE, radius=0.02) for x, y in df.values]  # Use only 500 points for animation
        
        # Shuffle for a natural appearance
        random.shuffle(dots)

        # Animate dots appearing in a wave-like manner
        # self.play(LaggedStart(*[FadeIn(dot) for dot in dots], lag_ratio=0.005))
        self.play(LaggedStart(*[Create(dot) for dot in dots], lag_ratio=0.005))

        # Hold final frame
        self.wait(2)

        # Add all dots to the scene for the final frame
        remaining_dots = [Dot(ax.c2p(x, y), color=BLUE, radius=0.02) for x, y in df.values]
        self.add(*remaining_dots)

class ScatterPlotScene(Scene):

    def construct(self):
        df = pl.read_parquet('merged_df.parquet')
        df = df[['adjusted_price_100ml', 'Duft.rating']].to_pandas()
        df = df[df['adjusted_price_100ml'] < 500]
        
        # Create Axes with labels
        ax = Axes(
            x_range=[0, 550, 50], 
            y_range=[0, 11, 1], 
            axis_config={"color": WHITE}
        )

        x_label = Tex(r"Adjusted Price per 100ml (€)", font_size=28).next_to(ax, DOWN, buff=0.5)
        y_label = Tex(r"Duft Rating", font_size=28)
        y_label.next_to(ax.y_axis.get_end(), UP, buff=0.3)  # Move above y-axis arrow

        # Title
        title = Tex(r"Perfume Price vs. Rating", font_size=36)
        title.to_edge(UP)

        # Add tick labels
        x_labels = VGroup(*[
            Tex(str(i), font_size=24).next_to(ax.c2p(i, 0), DOWN, buff=0.2)
            for i in range(0, 501, 50)
        ])
        y_labels = VGroup(*[
            Tex(str(i), font_size=24).next_to(ax.c2p(0, i), LEFT, buff=0.2)
            for i in range(0, 11, 1)
        ])

        # Add elements
        self.add(ax, x_label, y_label, title, x_labels, y_labels)

        # Scatter Plot Dots (Smaller Size)
        for x, y in df.values:
            dot = Dot(ax.c2p(x, y), color=BLUE, radius=0.03)  # Smaller dots
            self.add(dot)

# Execute rendering
if __name__ == "__main__":
    # os.system(r"manim -qk -v WARNING -p --disable_caching -o ScatterPlotScene.png Videos/scatterplot.py ScatterPlotScene")
    os.system(r"manim -qk -v WARNING -p --disable_caching -o ScatterPlotScene.mp4 Videos/scatterplot.py ScatterPlotAnimatedScene")