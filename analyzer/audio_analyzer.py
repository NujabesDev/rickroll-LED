#!/usr/bin/env python3
"""
Audio-to-LED Brightness Analyzer
Converts audio files into Arduino-compatible LED brightness data
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

class AudioLEDAnalyzer:
    def __init__(self):
        self.audio_data = None
        self.sample_rate = None
        self.duration = None
        
    def load_audio(self, filename):
        """Load audio file and extract data"""
        try:
            print(f"Loading {filename}...")
            
            self.audio_data, self.sample_rate = librosa.load(
                filename, 
                sr=None,
                mono=True
            )
            
            self.duration = len(self.audio_data) / self.sample_rate
            
            print(f"✓ Audio loaded successfully!")
            print(f"  Duration: {self.duration:.2f} seconds")
            
            return True
            
        except Exception as e:
            print(f"✗ Error loading audio: {e}")
            return False
    
    def calculate_brightness(self, window_ms=100):
        """Calculate LED brightness levels from audio volume"""
        if self.audio_data is None:
            print("No audio data loaded!")
            return []
        
        print(f"Analyzing audio volume...")
        
        window_samples = int(self.sample_rate * window_ms / 1000)
        energy_db = []
        
        for i in range(0, len(self.audio_data), window_samples):
            window = self.audio_data[i:i + window_samples]
            
            if len(window) == 0:
                break
                
            rms_energy = np.sqrt(np.mean(window ** 2))
            
            if rms_energy > 0:
                energy_in_db = 20 * np.log10(rms_energy)
            else:
                energy_in_db = -100
                
            energy_db.append(energy_in_db)
        
        energy_array = np.array(energy_db)
        
        # Dynamic range detection
        noise_floor = np.percentile(energy_array, 15)
        max_energy = np.percentile(energy_array, 85)
        
        print(f"  Noise floor: {noise_floor:.1f} dB")
        print(f"  Max energy: {max_energy:.1f} dB")
        print(f"  Dynamic range: {max_energy - noise_floor:.1f} dB")
        
        # Convert to brightness values (0-255)
        brightness_levels = []
        
        for energy in energy_db:
            if energy <= noise_floor:
                brightness = 0
            elif energy >= max_energy:
                brightness = 255
            else:
                normalized = (energy - noise_floor) / (max_energy - noise_floor)
                brightness = int(normalized * 255)
                
            brightness = max(0, min(255, brightness))
            brightness_levels.append(brightness)
        
        # Smooth to prevent flickering
        brightness_levels = self._smooth_brightness(brightness_levels)
        
        avg_brightness = np.mean([b for b in brightness_levels if b > 0])
        print(f"  Average brightness: {avg_brightness:.1f}/255")
        print(f"  Active time: {sum(1 for b in brightness_levels if b > 0)/len(brightness_levels)*100:.1f}%")
        
        return brightness_levels, energy_db
    
    def _smooth_brightness(self, brightness_levels, window_size=3):
        """Apply smoothing to reduce LED flickering"""
        smoothed = brightness_levels.copy()
        
        for i in range(len(brightness_levels)):
            start = max(0, i - window_size // 2)
            end = min(len(brightness_levels), i + window_size // 2 + 1)
            
            window_values = brightness_levels[start:end]
            smoothed[i] = int(np.mean(window_values))
        
        return smoothed
    
    def create_visualization(self, brightness_levels, energy_db, window_ms=100, output_file="audio_analysis.png"):
        """Generate and save visualization"""
        try:
            time_points = np.arange(len(brightness_levels)) * window_ms / 1000.0
            
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 10))
            
            # Waveform
            time_audio = np.linspace(0, self.duration, len(self.audio_data))
            ax1.plot(time_audio, self.audio_data, alpha=0.7, color='blue')
            ax1.set_title('Audio Waveform')
            ax1.set_ylabel('Amplitude')
            ax1.grid(True, alpha=0.3)
            
            # Energy levels
            ax2.plot(time_points, energy_db, color='orange', linewidth=1)
            ax2.set_title('Audio Energy (dB)')
            ax2.set_ylabel('Energy (dB)')
            ax2.grid(True, alpha=0.3)
            
            # LED brightness
            colors = plt.cm.viridis(np.array(brightness_levels) / 255.0)
            ax3.bar(time_points, brightness_levels, width=window_ms/1000.0, 
                   color=colors, alpha=0.8, edgecolor='none')
            ax3.set_title('LED Brightness Levels (0-255)')
            ax3.set_xlabel('Time (seconds)')
            ax3.set_ylabel('Brightness')
            ax3.set_ylim(0, 255)
            ax3.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"✓ Visualization saved: {output_file}")
            plt.close()
            
        except Exception as e:
            print(f"Could not create visualization: {e}")
    
    def export_arduino_data(self, brightness_levels, window_ms=100, output_file="brightness_data.h"):
        """Export brightness data as Arduino header file"""
        try:
            with open(output_file, 'w') as f:
                f.write("#ifndef BRIGHTNESS_DATA_H\n")
                f.write("#define BRIGHTNESS_DATA_H\n")
                f.write("#include <avr/pgmspace.h>\n\n")
                
                f.write("const unsigned char brightnessArray[] PROGMEM = {\n")
                
                # Write array data in rows of 16
                for i in range(0, len(brightness_levels), 16):
                    row = brightness_levels[i:i+16]
                    row_str = ", ".join(f"{b:3d}" for b in row)
                    time_str = f"{i * window_ms / 1000:.1f}s"
                    
                    if i + 16 < len(brightness_levels):
                        f.write(f"    {row_str},  // {time_str}\n")
                    else:
                        f.write(f"    {row_str}   // {time_str}\n")
                
                f.write("};\n")
                f.write(f"const int arraySize = {len(brightness_levels)};\n")
                f.write(f"const int ms = {window_ms};\n\n")
                f.write("#endif\n")
            
            print(f"✓ Arduino data exported: {output_file}")
            
            # Summary
            print(f"\n📊 Export Summary:")
            print(f"  Array size: {len(brightness_levels)} values")
            print(f"  Duration: {len(brightness_levels) * window_ms / 1000:.1f} seconds")
            print(f"  Time resolution: {window_ms}ms")
            avg_brightness = np.mean([b for b in brightness_levels if b > 0])
            print(f"  Average brightness: {avg_brightness:.1f}/255")
            
        except Exception as e:
            print(f"Error exporting data: {e}")

def main():
    print("🎵 Audio-to-LED Brightness Analyzer 🎵")
    print("Converts audio files into Arduino LED data")
    print("="*50)
    
    analyzer = AudioLEDAnalyzer()
    
    # Get filename
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Enter audio filename (MP3/WAV): ").strip()
    
    if not os.path.exists(filename):
        print(f"❌ File '{filename}' not found!")
        sys.exit(1)
    
    # Process audio
    if not analyzer.load_audio(filename):
        sys.exit(1)
    
    print("\n🔍 Analyzing audio...")
    brightness_levels, energy_levels = analyzer.calculate_brightness(window_ms=100)
    
    # Generate outputs
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    print("\n📈 Creating visualization...")
    analyzer.create_visualization(
        brightness_levels, 
        energy_levels, 
        100, 
        f"{base_name}_analysis.png"
    )
    
    print("\n💾 Exporting Arduino data...")
    analyzer.export_arduino_data(
        brightness_levels, 
        100, 
        "brightness_data.h"
    )
    
    print(f"\n✅ Done! Include 'brightness_data.h' in your Arduino project")
    print(f"📊 Check '{base_name}_analysis.png' for the visual analysis")

if __name__ == "__main__":
    main()