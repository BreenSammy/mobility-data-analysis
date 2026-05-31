"""Example script demonstrating classification pipeline usage"""

from pathlib import Path
import logging

from src.pipeline import ClassificationPipeline, UserProcessingPipeline
from src.data_manager import UserDataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    """Example: Train classifier on multiple users and predict"""

    # Setup
    base_data_dir = Path("data")
    processed_data_dir = base_data_dir / "processed"
    results_dir = Path("results")
    users = ["User1", "User2"]

    # Features for trip classification
    point_features = [
        "speed_ma",
        "acc_forw_ma",
        "acc_down_shift_ma",
        "trip_speed",
        "trip_duration",
    ]

    trip_features = [
        "median_speed",
        "std_speed",
        "std_acc_forw",
        "std_acc_down",
    ]

    # === TRIP Preprocessing ===
    print("\n" + "=" * 60)
    print("TRIP PREPROCESSING PIPELINE")
    print("=" * 60)

    for user in users:
        print(f"\n🔄 Preprocessing data for {user}...")
        data_manager = UserDataManager(
            user_id=user,
            raw_data_dir=base_data_dir / "raw",
            processed_data_dir=processed_data_dir,
            results_dir=results_dir,
        )
        if not data_manager.is_user_processed():
            UserProcessingPipeline(
                data_manager=data_manager, logger=logging.getLogger(f"Pipeline.{user}")
            ).run()
            print(f"✓ Preprocessing complete for {user}")
        else:
            print(f"✓ Data already preprocessed for {user}, skipping.")

    # === TRIP CLASSIFICATION ===
    print("\n" + "=" * 60)
    print("TRIP CLASSIFICATION PIPELINE")
    print("=" * 60)

    # Create data managers for each user
    data_managers = {
        user_id: UserDataManager(
            user_id, base_data_dir, processed_data_dir, results_dir
        )
        for user_id in users
    }

    # Create classification pipeline
    trip_pipeline = ClassificationPipeline(
        results_dir=results_dir, features=trip_features, classifier_type="trip"
    )

    # Train classifier on combined data from all users
    print("\n📊 Training trip classifier...")
    train_results = trip_pipeline.train(
        user_ids=users,
        data_managers=data_managers,
        n_neighbors=5,
    )
    print(f"✓ Training complete. Accuracy: {train_results['accuracy']:.4f}")

    # Make predictions for all users
    print("\n🎯 Making predictions for all users...")
    predictions = trip_pipeline.predict_all_users(users, data_managers)

    for user_id, pred_df in predictions.items():
        print(f"  {user_id}: {len(pred_df)} predictions")
        print(f"    Classes: {pred_df['predicted_class'].unique()}")

    # === POINT CLASSIFICATION ===
    print("\n" + "=" * 60)
    print("POINT CLASSIFICATION PIPELINE")
    print("=" * 60)

    point_pipeline = ClassificationPipeline(
        results_dir=results_dir, features=point_features, classifier_type="point"
    )

    print("\n📊 Training point classifier...")
    point_train_results = point_pipeline.train(
        user_ids=users,
        data_managers=data_managers,
        n_neighbors=3,
    )
    print(f"✓ Training complete. Accuracy: {point_train_results['accuracy']:.4f}")

    print("\n🎯 Making point predictions...")
    point_predictions = point_pipeline.predict_all_users(users, data_managers)

    for user_id, pred_df in point_predictions.items():
        print(f"  {user_id}: {len(pred_df)} point predictions")

    print("\n" + "=" * 60)
    print("✓ Classification pipeline complete!")
    print("=" * 60)
    print(f"\nResults saved to: {results_dir}")
    print(
        f"  Trip classifications: {results_dir}/User*/predictions/trip_classification.csv"
    )
    print(
        f"  Point classifications: {results_dir}/User*/predictions/point_classification.csv"
    )


if __name__ == "__main__":
    main()
