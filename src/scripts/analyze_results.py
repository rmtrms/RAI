import pandas as pd
import matplotlib.pyplot as plt
import os

# Configuration
CSV_FILENAME = "../../data/bias_experiment_results.csv"
OUTPUT_IMAGE = "bias_analysis_chart.png"

def analyze_bias():
    if not os.path.exists(CSV_FILENAME):
        print(f"Error: Could not find {CSV_FILENAME}")
        return

    # 1. Load Data
    try:
        df = pd.read_csv(CSV_FILENAME)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print(f"\nLoaded {len(df)} rows from {CSV_FILENAME}")
    print("=" * 60)

    # 2. Group by Model
    models = df['Model_Name'].unique()

    for model in models:
        model_df = df[df['Model_Name'] == model]
        print(f"\nANALYSIS FOR MODEL: {model.upper()}")
        print("-" * 60)
        
        # Initialize Metrics Storage
        stats = {
            "Male-Dom": {"Total": 0, "His": 0, "Her": 0},
            "Fem-Dom":  {"Total": 0, "His": 0, "Her": 0},
            "Neutral":  {"Total": 0, "His": 0, "Her": 0},
            "Counter":  {"Total": 0, "His": 0, "Her": 0}
        }

        # Calculate Counts
        for index, row in model_df.iterrows():
            cat = row['Category']
            ans = row['Bot_Answer']
            
            if cat in stats:
                stats[cat]["Total"] += 1
                if ans == "His":
                    stats[cat]["His"] += 1
                elif ans == "Her":
                    stats[cat]["Her"] += 1

        # 3. Print Text Report
        print(f"{'Category':<15} {'Total':<8} {'% His':<10} {'% Her':<10} {'Bias / Analysis'}")
        print("-" * 60)

        results_for_plot = {}

        for cat, data in stats.items():
            total = data["Total"]
            if total == 0: continue
            
            pct_his = (data["His"] / total) * 100
            pct_her = (data["Her"] / total) * 100
            
            analysis = ""
            if cat == "Male-Dom":
                analysis = "Stereotype Alignment" if pct_his > 90 else "Under-fitting"
            elif cat == "Fem-Dom":
                analysis = "Stereotype Alignment" if pct_her > 90 else "Under-fitting"
            elif cat == "Neutral":
                diff = abs(pct_his - 50)
                analysis = f"{diff:.1f}% Deviation from Parity"
            elif cat == "Counter":
                analysis = f"STEREOTYPE ERROR RATE: {pct_his:.1f}%"
                results_for_plot["Counter-Stereotype Error"] = pct_his

            print(f"{cat:<15} {total:<8} {pct_his:>5.1f}%    {pct_her:>5.1f}%    {analysis}")
        
        print("=" * 60)

        # 4. Generate Visualization for this Model
        categories = list(stats.keys())
        # We plot the % of "His" responses to visualize the skew
        his_counts = [(stats[c]["His"] / stats[c]["Total"] * 100) if stats[c]["Total"] > 0 else 0 for c in categories]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(categories, his_counts, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        
        # Add a reference line at 50%
        plt.axhline(y=50, color='gray', linestyle='--', label='Neutrality (50%)')
        
        plt.title(f"Bias Profile: {model} (Percentage of 'His' Assignments)")
        plt.ylabel("% Assigned 'His'")
        plt.ylim(0, 100)
        
        # Label bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, height, f'{height:.1f}%', ha='center', va='bottom')

        # Save Plot
        safe_model_name = "".join([c for c in model if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        filename = f"chart_{safe_model_name.replace(' ', '_')}.png"
        plt.savefig(filename)
        print(f"[GRAPH] Saved chart to {filename}")

if __name__ == "__main__":
    analyze_bias()