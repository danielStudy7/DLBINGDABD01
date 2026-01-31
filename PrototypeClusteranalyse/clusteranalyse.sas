%LET sourcePath = /home/u64420186/PrototypeSource;

/* Import */
DATA WORK.testData;
	LENGTH id $10 productId $10 charge $12 date $10;

	INFILE '&sourcePath/testData.csv' DELIMITER = ',' MISSOVER DSD FIRSTOBS = 2; 
	INFORMAT 	shouldRatePerMinute comma20.18
				currentRatePerMinute comma20.18;
	FORMAT 	currentRatePerMinute comma20.2;
	INPUT	id $
			productId $
			charge $
			date
			shouldRatePerMinute
			currentRatePerMinute;
RUN;

/* Daten vorbereiten */
PROC SORT DATA = WORK.testData OUT = WORK.testData_sorted;
	BY productId date;
RUN;

* Ausfälle identifizieren;
DATA WORK.testData_flagged;
	SET WORK.testData_sorted;
	
	diff = shouldRatePerMinute - currentRatePerMinute;
	
	*Hilfsvariable zur manuellen Kontrolle;
	isOutOfRange = (diff > 0.05)  or (diff < -0.05);
RUN;

/* Analyse */
PROC STANDARD DATA = WORK.testData_flagged MEAN = 0 STD = 1 OUT = WORK.testData_std;
	VAR shouldRatePerMinute currentRatePerMinute;
RUN;

*K-Means;
PROC FASTCLUS DATA = work.testData_std
	MAXCLUSTERS = 4
	MAXITER = 100
	OUT = WORK.testData_clustered_std
	OUTSEED = WORK.testData_centroids;
	VAR shouldRatePerMinute currentRatePerMinute;
RUN;

PROC SORT DATA = WORK.testData_clustered_std(KEEP=id cluster) OUT = WORK.cluster;
  	BY id;
RUN;

PROC SORT DATA = WORK.testData_flagged OUT = WORK.testData_flagged_sorted;
  	BY id;
RUN;

*Ur-Daten mit Clustern mergen;
DATA WORK.testData_clustered;
  	MERGE WORK.testData_flagged_sorted(in=a) WORK.cluster(in=b);
  	BY id;
  	IF a; 
RUN;

TITLE 'Clustergrößen';
PROC FREQ DATA = WORK.testData_clustered;
  	TABLES cluster / NOCUM;
RUN;

TITLE 'Clusterprofile';
PROC MEANS DATA = WORK.testData_clustered N MEAN STD MIN P25 MEDIAN P75 MAX;
  	CLASS cluster;
  	VAR shouldRatePerMinute currentRatePerMinute;
RUN;

PROC PRINCOMP DATA = WORK.testData_clustered_std OUT = WORK.qctestData_pca N=2;
  	VAR shouldRatePerMinute currentRatePerMinute;
RUN;

PROC SORT DATA = WORK.qctestData_pca; 
	BY id; 
RUN;

DATA WORK.testData_pca_plot;
  MERGE work.qctestData_pca(in=a) work.cluster(in=b);
  BY id;
  IF a;
RUN;

TITLE 'PCA-Raum Cluster';
PROC SGPLOT DATA = WORK.testData_pca_plot;
  SCATTER X = prin1 Y = prin2 / GROUP = cluster MARKERATTRS=(SIZE=8);
  XAXIS LABEL = 'PCA1';
  YAXIS LABEL = 'PCA2';
RUN;

TITLE;

ODS GRAPHICS OFF;

