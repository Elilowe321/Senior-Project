import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_squared_error,
    confusion_matrix,
)
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    GradientBoostingRegressor,
    GradientBoostingClassifier,
)
from sklearn.model_selection import train_test_split
from collections import OrderedDict
from joblib import dump


def gradient_boost(df):

    # Drop na columns if > 200 and other rows
    df = df.dropna(thresh=len(df) - 500, axis=1)
    df = df.dropna()
    print("Length of learning Data: ", len(df))

    # Create test and train data
    X_classification = df.drop(["target", "home_points", "away_points"], axis=1)
    y_classification = df["target"]  # Target variable: win

    X_regression = df.drop(["target", "home_points", "away_points"], axis=1)
    y_regression = df[
        ["home_points", "away_points"]
    ]  # Target variables: home and away scores

    # Split data into training and testing sets for classification and regression
    X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(
        X_classification, y_classification, test_size=0.2, random_state=42
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X_regression, y_regression, test_size=0.2, random_state=42
    )

    # Create models
    classification_model = GradientBoostingClassifier(n_estimators=100)
    regression_model_home = GradientBoostingRegressor(n_estimators=100)
    regression_model_away = GradientBoostingRegressor(n_estimators=100)

    # Fit models
    classification_model.fit(X_train_class, y_train_class)
    regression_model_home.fit(X_train, y_train["home_points"])
    regression_model_away.fit(X_train, y_train["away_points"])

    # Model Evaluation
    y_pred_class = classification_model.predict(X_test_class)
    y_pred_home = regression_model_home.predict(X_test)
    y_pred_away = regression_model_away.predict(X_test)

    # Check Accuracy
    classification_accuracy = accuracy_score(y_test_class, y_pred_class)
    mse_home = mean_squared_error(y_test["home_points"], y_pred_home)
    mse_away = mean_squared_error(y_test["away_points"], y_pred_away)

    # Save models
    dump(classification_model, filename="models/gradient_classification_model.joblib")
    dump(regression_model_home, filename="models/gradient_model_home.joblib")
    dump(regression_model_away, filename="models/gradient_model_away.joblib")

    # Return Model
    df = df.drop(["target", "home_points", "away_points"], axis=1)
    stats = {
        "classification_accuracy": classification_accuracy,
        "mse_home": mse_home,
        "mse_away": mse_away,
    }
    model = OrderedDict(
        {"model": "gradient boost", "stats": stats, "columns": df.columns.tolist()}
    )

    return model


def random_forest(df):

    # Drop na columns if > 200 and other rows
    df = df.dropna(thresh=len(df) - 500, axis=1)
    df = df.dropna()

    # Create test and train data
    X_classification = df.drop(["target", "home_points", "away_points"], axis=1)
    y_classification = df["target"]  # Target variable: win

    X_regression = df.drop(["target", "home_points", "away_points"], axis=1)
    y_regression = df[
        ["home_points", "away_points"]
    ]  # Target variables: home and away scores

    # Split data into training and testing sets for classification and regression
    X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(
        X_classification, y_classification, test_size=0.2, random_state=42
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X_regression, y_regression, test_size=0.2, random_state=42
    )

    # Create models
    classification_model = RandomForestClassifier(n_estimators=100)
    regression_model = RandomForestRegressor(n_estimators=100)

    # Fit models
    classification_model.fit(X_train_class, y_train_class)
    regression_model.fit(X_train, y_train)

    # Model Evaluation
    y_pred_class = classification_model.predict(X_test_class)
    y_pred = regression_model.predict(X_test)

    y_pred_home = y_pred[:, 0]
    y_pred_away = y_pred[:, 1]

    # Check Accuracy
    classification_accuracy = accuracy_score(y_test_class, y_pred_class)
    mse_home = mean_squared_error(y_test["home_points"], y_pred_home)
    mse_away = mean_squared_error(y_test["away_points"], y_pred_away)

    # Save models
    dump(
        classification_model,
        filename="models/random_forest_classification_model.joblib",
    )
    dump(regression_model, filename="models/random_forest_model.joblib")

    # Return Model
    df = df.drop(["target", "home_points", "away_points"], axis=1)
    stats = {
        "classification_accuracy": classification_accuracy,
        "mse_home": mse_home,
        "mse_away": mse_away,
    }
    model = OrderedDict(
        {"model": "random forest", "stats": stats, "columns": df.columns.tolist()}
    )

    return model


def user_created_model(user_id, name, df, description=None):

    print("Creating Model")

    # Drop na columns if > 200 and other rows
    df = df.dropna(thresh=len(df) - 500, axis=1)
    df = df.dropna()

    # Create test and train data
    X_classification = df.drop(["target", "home_points", "away_points"], axis=1)
    y_classification = df["target"]  # Target variable: win

    X_regression = df.drop(["target", "home_points", "away_points"], axis=1)
    y_regression = df[
        ["home_points", "away_points"]
    ]  # Target variables: home and away scores

    # Split data into training and testing sets for classification and regression
    X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(
        X_classification, y_classification, test_size=0.2, random_state=42
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X_regression, y_regression, test_size=0.2, random_state=42
    )

    # Create models
    classification_model = RandomForestClassifier(n_estimators=100)
    regression_model = RandomForestRegressor(n_estimators=100)

    # Fit models
    classification_model.fit(X_train_class, y_train_class)
    regression_model.fit(X_train, y_train)

    # Model Evaluation
    y_pred_class = classification_model.predict(X_test_class)
    y_pred = regression_model.predict(X_test)

    y_pred_home = y_pred[:, 0]
    y_pred_away = y_pred[:, 1]

    # Check Accuracy
    classification_accuracy = accuracy_score(y_test_class, y_pred_class)
    mse_home = mean_squared_error(y_test["home_points"], y_pred_home)
    mse_away = mean_squared_error(y_test["away_points"], y_pred_away)

    # Save models
    class_file_name = f"models/{user_id}_class_{name}.joblib"
    reg_file_name = f"models/{user_id}_reg_{name}.joblib"

    dump(classification_model, filename=class_file_name)
    dump(regression_model, filename=reg_file_name)

    # Return Model
    df = df.drop(["target", "home_points", "away_points"], axis=1)
    stats = {
        "classification_accuracy": classification_accuracy,
        "mse_home": mse_home,
        "mse_away": mse_away,
    }

    model = {
        "user_id": user_id,
        "name": name,
        "description": description,
        "file_location_class": class_file_name,
        "file_location_reg": reg_file_name,
        "columns": df.columns.tolist(),
        "stats": stats,
    }

    return model


def target_provided(user_id, name, df, type, target, description=None):

    if type == "classification":
        print("Creating Classification Model")

        # Drop na columns if > 200 and other rows
        # df = df.dropna(thresh=len(df) - 500, axis=1)
        df = df.dropna()

        x_model_name = df.drop([target], axis=1)  # TODO:: Fix home and away points
        y_model_name = df[target]  # Target variable: win

        # Split data into training and testing sets for classification and regression
        X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(
            x_model_name, y_model_name, test_size=0.2, random_state=42
        )

        # Create models
        classification_model = RandomForestClassifier(n_estimators=100)

        # Fit models
        classification_model.fit(X_train_class, y_train_class)

        # Model Evaluation
        y_pred_class = classification_model.predict(X_test_class)

        # Check Accuracy
        classification_accuracy = accuracy_score(y_test_class, y_pred_class)
        print("Classification Accuracy: ", classification_accuracy)

        # Save models
        class_file_name = f"models/{user_id}_class_{name}.joblib"
        dump(classification_model, filename=class_file_name)

        mse_home = None
        mse_away = None
        reg_file_name = None

        # Return Model
        # df = df.drop([target], axis=1)
        stats = {
            "classification_accuracy": round(classification_accuracy, 2),
            "mse_home": mse_home,
            "mse_away": mse_away,
        }

        model = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "type": type,
            "target": target,
            "file_location_class": class_file_name,
            "file_location_reg": reg_file_name,
            "columns": df.columns.tolist(),
            "stats": stats,
        }

        return model

    if type == "regression":
        target_home = f"home_{target}"
        target_away = f"away_{target}"

        print("Creating Regression Model")

        # Gradient Boost
        df = df.dropna()

        X_regression = df.drop([target_home, target_away], axis=1)
        y_regression = df[
            [target_home, target_away]
        ] 


        X_train, X_test, y_train, y_test = train_test_split(
            X_regression, y_regression, test_size=0.2, random_state=42
        )

        regression_model_home = GradientBoostingRegressor(n_estimators=100)
        regression_model_away = GradientBoostingRegressor(n_estimators=100)

        regression_model_home.fit(X_train, y_train[target_home])
        regression_model_away.fit(X_train, y_train[target_away])

        y_pred_home = regression_model_home.predict(X_test)
        y_pred_away = regression_model_away.predict(X_test)


        mse_home = mean_squared_error(y_test[target_home], y_pred_home)
        mse_away = mean_squared_error(y_test[target_away], y_pred_away)

        print("mse_home:", mse_home)

        reg_file_name_home = f"models/{user_id}_gradient_reg_home_{name}.joblib"
        reg_file_name_away = f"models/{user_id}_gradient_reg_away_{name}.joblib"

        dump(regression_model_home, filename=reg_file_name_home)
        dump(regression_model_away, filename=reg_file_name_away)

        classification_accuracy = None
        class_file_name = None

        stats = {
            "classification_accuracy": classification_accuracy,
            "mse_home": mse_home,
            "mse_away": mse_away,
        }

        model = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "type": type,
            "target": target,
            "file_location_class": class_file_name,
            "file_location_reg": reg_file_name_home,
            "columns": df.columns.tolist(),
            "stats": stats,
        }

        return model

        '''
        # THIS IS THE WORKING ONE FOR RANDOM FOREST
        
        # Drop na columns if > 200 and other rows
        # df = df.dropna(thresh=len(df) - 500, axis=1)
        df = df.dropna()

        x_model_name = df.drop([target_home, target_away], axis=1)
        y_model_name = df[[target_home, target_away]]

        X_train, X_test, y_train, y_test = train_test_split(
            x_model_name, y_model_name, test_size=0.2, random_state=42
        )

        # Create models
        regression_model = RandomForestRegressor(n_estimators=100)

        # Fit models
        regression_model.fit(X_train, y_train)

        # Model Evaluation
        y_pred = regression_model.predict(X_test)

        y_pred_home = y_pred[:, 0]
        y_pred_away = y_pred[:, 1]

        # Check Accuracy
        mse_home = mean_squared_error(y_test[target_home], y_pred_home)
        mse_away = mean_squared_error(y_test[target_away], y_pred_away)

        print("MSE Home: ", mse_home)
        print("MSE Away: ", mse_away)

        # Save models
        reg_file_name = f"models/{user_id}_reg_{name}.joblib"

        dump(regression_model, filename=reg_file_name)

        classification_accuracy = None
        class_file_name = None

        # Return Model
        # df = df.drop([target_home, target_away], axis=1)
        stats = {
            "classification_accuracy": classification_accuracy,
            "mse_home": mse_home,
            "mse_away": mse_away,
        }

        model = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "type": type,
            "target": target,
            "file_location_class": class_file_name,
            "file_location_reg": reg_file_name,
            "columns": df.columns.tolist(),
            "stats": stats,
        }

        return model
        '''
