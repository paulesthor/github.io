setwd("C:/Users/nolan/OneDrive - Université de Poitiers/S2/SAE/STAT")

train <- read.csv2("train.csv")
test <- read.csv2("test.csv")

############# Modèle Maison (linéaire) #############

# Filtrer pour ne garder que les maisons
train_maisons <- subset(train, Type.local == "Maison")
test_maisons <- subset(test, Type.local == "Maison")

# Calculer le prix moyen au m² par commune en utilisant un modèle linéaire
prix_m2_commune_maisons <- aggregate(Valeur.fonciere / Surface.reelle.bati ~ Commune, data = train_maisons, FUN = function(x) {
  model <- lm(x ~ 1)
  coef(model)[1]  # Coefficient A 
})
names(prix_m2_commune_maisons) <- c("Commune", "prix_m2_moyen")

# Fusionner avec le fichier test
predictions_maisons <- merge(test_maisons, prix_m2_commune_maisons, by = "Commune", all.x = TRUE)

# Calculer la valeur prédite pour chaque maison
predictions_maisons$valeur_predite <- predictions_maisons$prix_m2_moyen * predictions_maisons$Surface.reelle.bati

# Modèle linéaire global (toutes les maisons)
modele_global_maisons <- lm(Valeur.fonciere ~ Surface.reelle.bati, data = train_maisons)
A_global_maisons <- coef(modele_global_maisons)[1]  # Intercept
B_global_maisons <- coef(modele_global_maisons)[2]  # Pente

# Appliquer le modèle linéaire global pour les maisons
predictions_maisons$valeur_predite_global <- A_global_maisons + B_global_maisons * predictions_maisons$Surface.reelle.bati

# Convertir la colonne Date.mutation en date et extraire l'année
predictions_maisons$Date.mutation <- as.Date(predictions_maisons$Date.mutation, format = "%d/%m/%Y")
predictions_maisons$annee_mutation <- format(predictions_maisons$Date.mutation, "%Y")

# Calculer le taux d'évolution entre 2023 et 2024
valeurs_2023_maisons <- subset(train_maisons, format(as.Date(Date.mutation, format = "%d/%m/%Y"), "%Y") == "2023")
valeurs_2024_maisons <- subset(train_maisons, format(as.Date(Date.mutation, format = "%d/%m/%Y"), "%Y") == "2024")

moyenne_2023_maisons <- mean(valeurs_2023_maisons$Valeur.fonciere, na.rm = TRUE)
moyenne_2024_maisons <- mean(valeurs_2024_maisons$Valeur.fonciere, na.rm = TRUE)

taux_evolution_maisons <- ifelse(!is.na(moyenne_2023_maisons) & !is.na(moyenne_2024_maisons) & moyenne_2023_maisons != 0, 
                                 moyenne_2024_maisons / moyenne_2023_maisons, 1)

# Appliquer le taux d'évolution pour les ventes en 2024 (maisons)
predictions_maisons$valeur_predite <- ifelse(predictions_maisons$annee_mutation == "2024", 
                                             predictions_maisons$valeur_predite * taux_evolution_maisons, 
                                             predictions_maisons$valeur_predite)


############# Modèle Appartement (linéaire) #############

# Filtrer pour ne garder que les appartements
train_appartements <- subset(train, Type.local == "Appartement")
test_appartements <- subset(test, Type.local == "Appartement")

# Calculer le prix moyen au m² par commune et par nombre de pièces principales
prix_m2_commune_pieces <- aggregate(Valeur.fonciere / Surface.reelle.bati ~ Commune + Nombre.pieces.principales, 
                                    data = train_appartements, FUN = function(x) {
                                      model <- lm(x ~ 1)
                                      coef(model)[1]  # Coefficient A 
                                    })
names(prix_m2_commune_pieces) <- c("Commune", "Nombre.pieces.principales", "prix_m2_moyen")

# Fusionner avec le fichier test pour les appartements
predictions_appartements <- merge(test_appartements, prix_m2_commune_pieces, by = c("Commune", "Nombre.pieces.principales"), all.x = TRUE)

# Calculer la valeur prédite pour chaque appartement
predictions_appartements$valeur_predite <- predictions_appartements$prix_m2_moyen * predictions_appartements$Surface.reelle.bati

# Modèle linéaire global (tous les appartements)
modele_global_appartements <- lm(Valeur.fonciere ~ Surface.reelle.bati, data = train_appartements)
A_global_appartements <- coef(modele_global_appartements)[1]  # Intercept
B_global_appartements <- coef(modele_global_appartements)[2]  # Pente

# Appliquer le modèle linéaire global pour les appartements
predictions_appartements$valeur_predite_global <- A_global_appartements + B_global_appartements * predictions_appartements$Surface.reelle.bati

# Convertir la colonne Date.mutation en date et extraire l'année
predictions_appartements$Date.mutation <- as.Date(predictions_appartements$Date.mutation, format = "%d/%m/%Y")
predictions_appartements$annee_mutation <- format(predictions_appartements$Date.mutation, "%Y")

# Calculer le taux d'évolution entre 2023 et 2024 pour les appartements
valeurs_2023_appartements <- subset(train_appartements, format(as.Date(Date.mutation, format = "%d/%m/%Y"), "%Y") == "2023")
valeurs_2024_appartements <- subset(train_appartements, format(as.Date(Date.mutation, format = "%d/%m/%Y"), "%Y") == "2024")

moyenne_2023_appartements <- mean(valeurs_2023_appartements$Valeur.fonciere, na.rm = TRUE)
moyenne_2024_appartements <- mean(valeurs_2024_appartements$Valeur.fonciere, na.rm = TRUE)

taux_evolution_appartements <- ifelse(!is.na(moyenne_2023_appartements) & !is.na(moyenne_2024_appartements) & moyenne_2023_appartements != 0, 
                                      moyenne_2024_appartements / moyenne_2023_appartements, 1)

# Appliquer le taux d'évolution pour les ventes en 2024 (appartements)
predictions_appartements$valeur_predite <- ifelse(predictions_appartements$annee_mutation == "2024", 
                                                  predictions_appartements$valeur_predite * taux_evolution_appartements, 
                                                  predictions_appartements$valeur_predite)

############# Combiner les résultats #############

# Ajouter un identifiant de type de bien pour la distinction
predictions_maisons$Type.local <- "Maison"
predictions_appartements$Type.local <- "Appartement"

# Fusionner les prédictions des maisons et des appartements dans un seul dataframe
predictions_final <- rbind(predictions_maisons[, c("id", "valeur_predite")], 
                           predictions_appartements[, c("id", "valeur_predite")])

# Trier les résultats selon l'ordre du fichier test
predictions_final <- predictions_final[match(test$id, predictions_final$id), ]

# Enregistrer les résultats dans un seul fichier CSVS
write.csv2(predictions_final, "prediction.csv", row.names = FALSE)
