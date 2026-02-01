"""
Command-line interface for the AI Matchmaker application.

Provides commands for training, matchmaking, and simulation phases.
"""

import sys
import argparse
from typing import Optional
from pathlib import Path

from .utils.config import get_config
from .utils.logging import setup_logging, get_logger
from .utils.exceptions import AIMatchmakerError, ConfigurationError

logger = get_logger(__name__)


def setup_cli_logging(verbose: bool = False, log_file: Optional[str] = None):
    """Set up logging for CLI usage."""
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level=log_level, log_file=log_file)


def check_configuration():
    """Check if the application is properly configured."""
    try:
        config = get_config()
        
        # Check for required API keys
        if not config.api.gemini_api_key:
            raise ConfigurationError(
                "Gemini API key not found. Please set GEMINI_API_KEY environment variable."
            )
        
        # Check if required directories exist
        config.ensure_directories()
        
        logger.info("Configuration check passed")
        return True
        
    except Exception as e:
        logger.error(f"Configuration check failed: {e}")
        return False


def cmd_config(args):
    """Handle config command."""
    if args.check:
        success = check_configuration()
        sys.exit(0 if success else 1)
    
    # Show current configuration
    config = get_config()
    print("AI Matchmaker Configuration:")
    print(f"  Environment: {config.environment}")
    print(f"  Log Level: {config.log_level}")
    print(f"  Debug Mode: {config.debug}")
    print(f"  Default Language: {config.localization.default_language}")
    print(f"  Supported Languages: {', '.join(config.localization.supported_languages_list)}")
    print(f"  Database Path: {config.database.chroma_db_path}")


def cmd_train(args):
    """Handle train command."""
    logger.info(f"Starting training for user: {args.user_id}")
    # TODO: Implement training workflow
    print(f"Training mode for user {args.user_id} - Implementation pending")


def cmd_match(args):
    """Handle match command."""
    logger.info(f"Starting matchmaking between users: {args.user1} and {args.user2}")
    # TODO: Implement matchmaking workflow
    print(f"Matchmaking between {args.user1} and {args.user2} - Implementation pending")


def cmd_simulate(args):
    """Handle simulate command."""
    logger.info(f"Starting simulation for users: {args.user1} and {args.user2}")
    # TODO: Implement simulation workflow
    print(f"Simulation for {args.user1} and {args.user2} - Implementation pending")


def create_parser():
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="AI Matchmaker - Multi-agent matchmaking system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-matchmaker config --check          Check configuration
  ai-matchmaker train user123           Start training for user
  ai-matchmaker match user1 user2       Start matchmaking session
  ai-matchmaker simulate user1 user2    Start simulation session
        """
    )
    
    # Global options
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log to file instead of console"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument(
        "--check",
        action="store_true",
        help="Check configuration validity"
    )
    config_parser.set_defaults(func=cmd_config)
    
    # Train command
    train_parser = subparsers.add_parser("train", help="Start user training")
    train_parser.add_argument("user_id", help="User ID to train")
    train_parser.add_argument(
        "--language",
        default="en",
        help="Language for training session (default: en)"
    )
    train_parser.set_defaults(func=cmd_train)
    
    # Match command
    match_parser = subparsers.add_parser("match", help="Start matchmaking session")
    match_parser.add_argument("user1", help="First user ID")
    match_parser.add_argument("user2", help="Second user ID")
    match_parser.add_argument(
        "--max-turns",
        type=int,
        default=20,
        help="Maximum conversation turns (default: 20)"
    )
    match_parser.set_defaults(func=cmd_match)
    
    # Simulate command
    simulate_parser = subparsers.add_parser("simulate", help="Start simulation session")
    simulate_parser.add_argument("user1", help="First user ID")
    simulate_parser.add_argument("user2", help="Second user ID")
    simulate_parser.add_argument(
        "--scenarios",
        type=int,
        default=5,
        help="Number of scenarios to run (default: 5)"
    )
    simulate_parser.set_defaults(func=cmd_simulate)
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    setup_cli_logging(verbose=args.verbose, log_file=args.log_file)
    
    try:
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
    
    except AIMatchmakerError as e:
        logger.error(f"Application error: {e.message}")
        if args.verbose:
            logger.error(f"Error details: {e.context}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()