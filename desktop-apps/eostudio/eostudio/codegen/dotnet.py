""".NET application code generator for EoStudio UI components.

Supported targets: MAUI (XAML + C#), WPF (XAML + C# MVVM), WinUI 3 (XAML + C#).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


class DotNetAppGenerator:
    """Generates .NET application source files from EoStudio screens."""

    SUPPORTED_TARGETS = ("maui", "wpf", "winui")

    COMPONENT_MAPS: Dict[str, Dict[str, str]] = {
        "maui": {
            "Button": "Button", "Text": "Label", "Input": "Entry",
            "Container": "VerticalStackLayout", "Card": "Frame",
            "AppBar": "Shell", "List": "CollectionView", "Grid": "Grid",
            "Image": "Image", "Dialog": "ContentPage", "TabBar": "TabBar",
        },
        "wpf": {
            "Button": "Button", "Text": "TextBlock", "Input": "TextBox",
            "Container": "StackPanel", "Card": "GroupBox",
            "AppBar": "Menu", "List": "ListBox", "Grid": "UniformGrid",
            "Image": "Image", "Dialog": "Window", "TabBar": "TabControl",
        },
        "winui": {
            "Button": "Button", "Text": "TextBlock", "Input": "TextBox",
            "Container": "StackPanel", "Card": "Expander",
            "AppBar": "NavigationView", "List": "ListView", "Grid": "GridView",
            "Image": "Image", "Dialog": "ContentDialog", "TabBar": "TabView",
        },
    }

    def __init__(self, target: str = "maui") -> None:
        if target not in self.SUPPORTED_TARGETS:
            raise ValueError(f"Unknown target {target!r}. "
                             f"Supported: {', '.join(self.SUPPORTED_TARGETS)}")
        self._target = target

    def generate(self, screens: List[Dict[str, Any]],
                 app_name: str = "EoStudioApp") -> Dict[str, str]:
        if not screens:
            screens = [{"name": "Home", "components": []}]
        dispatch = {"maui": self._gen_maui, "wpf": self._gen_wpf,
                    "winui": self._gen_winui}
        return dispatch[self._target](screens, app_name)

    # -- MAUI ---------------------------------------------------------

    def _gen_maui(self, screens: List[Dict[str, Any]],
                  app_name: str) -> Dict[str, str]:
        files: Dict[str, str] = {}
        files[f"{app_name}.csproj"] = self._maui_csproj(app_name)
        files["MauiProgram.cs"] = self._maui_program(app_name)
        files["AppShell.xaml"] = self._maui_shell_xaml(screens, app_name)
        files["AppShell.xaml.cs"] = (
            f"namespace {self._ns(app_name)};\n\n"
            f"public partial class AppShell : Shell\n{{\n"
            f"    public AppShell() => InitializeComponent();\n}}\n")
        for s in screens:
            name = self._pascal(s.get("name", "Home"))
            body = self._maui_xaml_components(s.get("components", []), 3)
            files[f"Views/{name}Page.xaml"] = (
                f'<?xml version="1.0" encoding="utf-8" ?>\n'
                f'<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"\n'
                f'             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"\n'
                f'             x:Class="{self._ns(app_name)}.Views.{name}Page"\n'
                f'             Title="{name}">\n'
                f'    <ScrollView>\n'
                f'        <VerticalStackLayout Padding="16" Spacing="12">\n'
                f'            <Label Text="{name}" FontSize="24" FontAttributes="Bold" />\n'
                f'{body}'
                f'        </VerticalStackLayout>\n'
                f'    </ScrollView>\n'
                f'</ContentPage>\n')
            files[f"Views/{name}Page.xaml.cs"] = (
                f"namespace {self._ns(app_name)}.Views;\n\n"
                f"public partial class {name}Page : ContentPage\n{{\n"
                f"    public {name}Page() => InitializeComponent();\n}}\n")
        return files

    def _maui_xaml_components(self, components: List[Dict[str, Any]],
                              indent: int) -> str:
        lines: List[str] = []
        pad = "    " * indent
        for c in components:
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", ""))
            ch = c.get("children", [])
            if ct == "Button":
                lines.append(f'{pad}<Button Text="{lb}" />\n')
            elif ct == "Text":
                lines.append(f'{pad}<Label Text="{lb}" />\n')
            elif ct == "Input":
                lines.append(f'{pad}<Entry Placeholder="{lb}" />\n')
            elif ct == "Card":
                inner = self._maui_xaml_components(ch, indent + 1) if ch else f'{pad}    <Label Text="{lb}" />\n'
                lines.append(f'{pad}<Frame Padding="12" CornerRadius="8">\n'
                             f'{pad}    <VerticalStackLayout Spacing="8">\n{inner}'
                             f'{pad}    </VerticalStackLayout>\n{pad}</Frame>\n')
            elif ct == "Image":
                src = c.get("src", "dotnet_bot.png")
                lines.append(f'{pad}<Image Source="{src}" HeightRequest="200" />\n')
            elif ct == "Container" and ch:
                d = c.get("direction", "column")
                tag = "HorizontalStackLayout" if d == "row" else "VerticalStackLayout"
                inner = self._maui_xaml_components(ch, indent + 1)
                lines.append(f'{pad}<{tag} Spacing="8">\n{inner}{pad}</{tag}>\n')
            else:
                lines.append(f'{pad}<Label Text="{lb}" />\n')
        return "".join(lines)

    def _maui_shell_xaml(self, screens: List[Dict[str, Any]],
                         app_name: str) -> str:
        tabs = ""
        for s in screens:
            name = self._pascal(s.get("name", "Home"))
            tabs += (f'        <ShellContent Title="{name}"\n'
                     f'                      ContentTemplate="{{DataTemplate local:Views.{name}Page}}" />\n')
        return (f'<?xml version="1.0" encoding="utf-8" ?>\n'
                f'<Shell xmlns="http://schemas.microsoft.com/dotnet/2021/maui"\n'
                f'       xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"\n'
                f'       xmlns:local="clr-namespace:{self._ns(app_name)}"\n'
                f'       x:Class="{self._ns(app_name)}.AppShell"\n'
                f'       Title="{app_name}">\n'
                f'    <TabBar>\n{tabs}    </TabBar>\n</Shell>\n')

    def _maui_csproj(self, app_name: str) -> str:
        return ('<Project Sdk="Microsoft.NET.Sdk">\n'
                '  <PropertyGroup>\n'
                '    <TargetFrameworks>net8.0-android;net8.0-ios;net8.0-maccatalyst</TargetFrameworks>\n'
                '    <OutputType>Exe</OutputType>\n'
                '    <UseMaui>true</UseMaui>\n'
                '    <SingleProject>true</SingleProject>\n'
                f'    <RootNamespace>{self._ns(app_name)}</RootNamespace>\n'
                '  </PropertyGroup>\n</Project>\n')

    def _maui_program(self, app_name: str) -> str:
        return (f"namespace {self._ns(app_name)};\n\n"
                "public static class MauiProgram\n{\n"
                "    public static MauiApp CreateMauiApp()\n    {\n"
                "        var builder = MauiApp.CreateBuilder();\n"
                "        builder.UseMauiApp<App>();\n"
                "        return builder.Build();\n    }\n}\n")

    # -- WPF ----------------------------------------------------------

    def _gen_wpf(self, screens: List[Dict[str, Any]],
                 app_name: str) -> Dict[str, str]:
        files: Dict[str, str] = {}
        files[f"{app_name}.csproj"] = (
            '<Project Sdk="Microsoft.NET.Sdk">\n'
            '  <PropertyGroup>\n'
            '    <OutputType>WinExe</OutputType>\n'
            '    <TargetFramework>net8.0-windows</TargetFramework>\n'
            '    <UseWPF>true</UseWPF>\n'
            f'    <RootNamespace>{self._ns(app_name)}</RootNamespace>\n'
            '  </PropertyGroup>\n</Project>\n')

        tab_items = ""
        for s in screens:
            name = self._pascal(s.get("name", "Home"))
            body = self._wpf_xaml_components(s.get("components", []), 5)
            tab_items += (f'            <TabItem Header="{name}">\n'
                          f'                <ScrollViewer>\n'
                          f'                    <StackPanel Margin="16">\n'
                          f'                        <TextBlock Text="{name}" FontSize="24" FontWeight="Bold" Margin="0,0,0,12" />\n'
                          f'{body}'
                          f'                    </StackPanel>\n'
                          f'                </ScrollViewer>\n'
                          f'            </TabItem>\n')

        files["MainWindow.xaml"] = (
            f'<Window x:Class="{self._ns(app_name)}.MainWindow"\n'
            f'        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"\n'
            f'        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"\n'
            f'        Title="{app_name}" Width="1200" Height="800">\n'
            f'    <DockPanel>\n'
            f'        <Menu DockPanel.Dock="Top">\n'
            f'            <MenuItem Header="_File"><MenuItem Header="Exit" Click="Exit_Click" /></MenuItem>\n'
            f'        </Menu>\n'
            f'        <StatusBar DockPanel.Dock="Bottom"><StatusBarItem Content="Ready" /></StatusBar>\n'
            f'        <TabControl>\n{tab_items}'
            f'        </TabControl>\n'
            f'    </DockPanel>\n</Window>\n')

        files["MainWindow.xaml.cs"] = (
            "using System.Windows;\n\n"
            f"namespace {self._ns(app_name)}\n{{\n"
            "    public partial class MainWindow : Window\n    {\n"
            "        public MainWindow() => InitializeComponent();\n"
            "        private void Exit_Click(object s, RoutedEventArgs e) => Close();\n"
            "    }\n}\n")
        return files

    def _wpf_xaml_components(self, components: List[Dict[str, Any]],
                             indent: int) -> str:
        lines: List[str] = []
        pad = "    " * indent
        for c in components:
            ct = c.get("type", "Container")
            lb = c.get("label", c.get("text", ""))
            ch = c.get("children", [])
            if ct == "Button":
                lines.append(f'{pad}<Button Content="{lb}" Padding="8" Margin="0,4" />\n')
            elif ct == "Text":
                lines.append(f'{pad}<TextBlock Text="{lb}" Margin="0,4" />\n')
            elif ct == "Input":
                lines.append(f'{pad}<TextBox Margin="0,4" />\n')
            elif ct == "Card":
                inner = self._wpf_xaml_components(ch, indent + 1) if ch else f'{pad}    <TextBlock Text="{lb}" />\n'
                lines.append(f'{pad}<GroupBox Header="{lb}" Padding="8" Margin="0,4">\n'
                             f'{pad}    <StackPanel>\n{inner}{pad}    </StackPanel>\n{pad}</GroupBox>\n')
            elif ct == "Container" and ch:
                d = c.get("direction", "column")
                orient = ' Orientation="Horizontal"' if d == "row" else ""
                inner = self._wpf_xaml_components(ch, indent + 1)
                lines.append(f'{pad}<StackPanel{orient} Margin="0,4">\n{inner}{pad}</StackPanel>\n')
            else:
                lines.append(f'{pad}<TextBlock Text="{lb}" Margin="0,4" />\n')
        return "".join(lines)

    # -- WinUI --------------------------------------------------------

    def _gen_winui(self, screens: List[Dict[str, Any]],
                   app_name: str) -> Dict[str, str]:
        files: Dict[str, str] = {}
        files[f"{app_name}.csproj"] = (
            '<Project Sdk="Microsoft.NET.Sdk">\n'
            '  <PropertyGroup>\n'
            '    <OutputType>WinExe</OutputType>\n'
            '    <TargetFramework>net8.0-windows10.0.19041.0</TargetFramework>\n'
            '    <UseWinUI>true</UseWinUI>\n'
            f'    <RootNamespace>{self._ns(app_name)}</RootNamespace>\n'
            '  </PropertyGroup>\n</Project>\n')

        nav_items = ""
        for s in screens:
            name = self._pascal(s.get("name", "Home"))
            nav_items += f'                <NavigationViewItem Content="{name}" Tag="{name}" />\n'

        pages = "                "
        for i, s in enumerate(screens):
            name = self._pascal(s.get("name", "Home"))
            body = self._wpf_xaml_components(s.get("components", []), 5)
            files[f"Views/{name}Page.xaml"] = (
                f'<Page x:Class="{self._ns(app_name)}.Views.{name}Page"\n'
                f'      xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"\n'
                f'      xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">\n'
                f'    <ScrollViewer>\n'
                f'        <StackPanel Padding="16" Spacing="12">\n'
                f'            <TextBlock Text="{name}" Style="{{StaticResource TitleTextBlockStyle}}" />\n'
                f'{body}'
                f'        </StackPanel>\n'
                f'    </ScrollViewer>\n</Page>\n')
            files[f"Views/{name}Page.xaml.cs"] = (
                f"namespace {self._ns(app_name)}.Views;\n\n"
                f"public sealed partial class {name}Page : Microsoft.UI.Xaml.Controls.Page\n{{\n"
                f"    public {name}Page() => this.InitializeComponent();\n}}\n")

        files["MainWindow.xaml"] = (
            f'<Window x:Class="{self._ns(app_name)}.MainWindow"\n'
            f'        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"\n'
            f'        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"\n'
            f'        Title="{app_name}">\n'
            f'    <NavigationView>\n'
            f'        <NavigationView.MenuItems>\n{nav_items}'
            f'        </NavigationView.MenuItems>\n'
            f'        <Frame x:Name="ContentFrame" />\n'
            f'    </NavigationView>\n</Window>\n')
        files["MainWindow.xaml.cs"] = (
            f"namespace {self._ns(app_name)};\n\n"
            "public sealed partial class MainWindow : Microsoft.UI.Xaml.Window\n{\n"
            "    public MainWindow() => this.InitializeComponent();\n}\n")
        return files

    # -- Helpers ------------------------------------------------------

    @staticmethod
    def _pascal(name: str) -> str:
        return "".join(w.capitalize() for w in re.split(r"[\s_\-]+", name) if w)

    @staticmethod
    def _ns(name: str) -> str:
        clean = re.sub(r"[^A-Za-z0-9]", "", name)
        return clean or "App"
