"""
Command Line Interface for ContractQuard Static Analyzer MVP.
"""

import sys
import click
from pathlib import Path
from typing import Optional

from .core.config import Config
from .core.analyzer import ContractQuardAnalyzer
from .core.findings import Severity


@click.group()
@click.version_option(version="0.1.0")
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="Path to configuration file"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output"
)
@click.pass_context
def cli(ctx, config: Optional[str], verbose: bool):
    """
    ContractQuard Static Analyzer MVP
    
    AI-augmented smart contract security analysis tool by QuantLink.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Load configuration
    if config:
        ctx.obj['config'] = Config.load_from_file(config)
    else:
        ctx.obj['config'] = Config()
    
    # Override verbose setting if specified
    if verbose:
        ctx.obj['config'].output.verbose = True


@cli.command()
@click.argument('target', type=click.Path(exists=True))
@click.option(
    '--output', '-o',
    type=click.Path(),
    help='Output file path (default: stdout)'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['console', 'json', 'html', 'markdown']),
    default='console',
    help='Output format'
)
@click.option(
    '--severity', '-s',
    type=click.Choice(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']),
    default='INFO',
    help='Minimum severity level to report'
)
@click.option(
    '--recursive', '-r',
    is_flag=True,
    help='Recursively analyze subdirectories'
)
@click.option(
    '--include-tests',
    is_flag=True,
    help='Include test files in analysis'
)
@click.pass_context
def analyze(ctx, target: str, output: Optional[str], format: str, 
           severity: str, recursive: bool, include_tests: bool):
    """
    Analyze Solidity smart contract files for security vulnerabilities.
    
    TARGET can be a single .sol file or a directory containing Solidity files.
    """
    config = ctx.obj['config']
    
    # Override configuration with CLI options
    config.output.format = format
    config.output.output_file = output
    config.min_severity = severity
    config.include_test_files = include_tests
    
    try:
        # Initialize analyzer
        analyzer = ContractQuardAnalyzer(config)
        
        # Run analysis
        click.echo(f"Starting analysis of: {target}")
        results = analyzer.run_analysis(target)
        
        # Output results
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(results['report'])
            click.echo(f"Report saved to: {output}")
        else:
            click.echo(results['report'])
        
        # Print summary statistics
        stats = results['statistics']
        click.echo(f"\n📊 Analysis Summary:")
        click.echo(f"   Total findings: {stats['total_findings']}")
        click.echo(f"   Files analyzed: {stats['files_analyzed']}")
        click.echo(f"   Analysis time: {stats['analysis_time_seconds']}s")
        
        # Print severity breakdown
        severity_breakdown = stats['severity_breakdown']
        if any(count > 0 for count in severity_breakdown.values()):
            click.echo(f"\n🔍 Severity Breakdown:")
            for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
                count = severity_breakdown.get(sev, 0)
                if count > 0:
                    severity_obj = Severity(sev)
                    click.echo(f"   {severity_obj.color_code}{sev}{severity_obj.reset_code}: {count}")
        
        # Exit with appropriate code
        critical_count = severity_breakdown.get('CRITICAL', 0)
        high_count = severity_breakdown.get('HIGH', 0)
        
        if critical_count > 0:
            sys.exit(2)  # Critical issues found
        elif high_count > 0:
            sys.exit(1)  # High severity issues found
        else:
            sys.exit(0)  # Success
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(3)


@cli.command()
@click.option(
    '--output', '-o',
    type=click.Path(),
    default='contractquard.yaml',
    help='Output configuration file path'
)
def init_config(output: str):
    """
    Generate a default configuration file.
    """
    try:
        config = Config()
        config.save_to_file(output)
        click.echo(f"✅ Default configuration saved to: {output}")
        click.echo("Edit this file to customize your analysis settings.")
    except Exception as e:
        click.echo(f"❌ Error creating configuration: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def list_detectors():
    """
    List all available vulnerability detectors.
    """
    try:
        from .detectors.registry import DetectorRegistry
        
        config = Config()
        registry = DetectorRegistry(config)
        detectors = registry.get_all_detectors()
        
        click.echo("📋 Available Detectors:")
        click.echo("=" * 50)
        
        for detector in detectors:
            status = "✅ Enabled" if detector.enabled else "❌ Disabled"
            click.echo(f"\n🔍 {detector.name}")
            click.echo(f"   Status: {status}")
            click.echo(f"   Description: {detector.description}")
            click.echo(f"   Targets: {', '.join(detector.vulnerability_types)}")
            
    except Exception as e:
        click.echo(f"❌ Error listing detectors: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def validate(file_path: str):
    """
    Validate Solidity syntax without running security analysis.
    """
    try:
        from .parsers.solidity_parser import SolidityParser
        from .core.config import SolcConfig
        
        parser = SolidityParser(SolcConfig())
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        click.echo(f"Validating: {file_path}")
        parsed_data = parser.parse(source_code, file_path)
        
        if parsed_data:
            click.echo("✅ Syntax validation passed")
        else:
            click.echo("❌ Syntax validation failed")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Validation error: {str(e)}", err=True)
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n⚠️  Analysis interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
