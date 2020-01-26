# Kap_01_funktions.py
# TODO: Übernahme der alten IMS Datenstrukturen aus 1993
#! Funktionen für die Ausführung in Notebook des Kapitels1


'''
/* ***************************************************************** */
/*                                                                   */
/*   Datenstrukturen, Deklarationen und Konstanten von IMS           */
/*                                                                   */
/* ***************************************************************** */
#if defined(PC386)
 #define version   "MSDOS v1.0"
#elif defined(UNIX)
 #define version   "UNIX  v1.0"
#else
 #define version   "UNDE. v1.0"
#endif
#include <stdio.h>                                                       
#define SIMLAENGE  100 /* maximale Perioden pro Simulationslauf      */
#define MAXVU      25  /* maximale Anzahl aktiver Versicherer        */
#define MAXVN      200 /* maximale Anzahl aktiver Versicherungsnehmer*/
#define MAXSPARTEN 2   /* maximale Anzahl der Sparten einer VU       */
#define MAXRISKS   2   /* maximale Anzahl von Risiken eines VN       */
#define MAXDATEI   10  /* maximale Anzahl gleichzeitig offener Files */
#define MAXGNUDT   4   /* maximale Anzahl GNUplot Steuerfiles        */
/* ***************************************************************** */
/* Deklaration der Dateivariablen fuer die Datein, in die die        */
/* Ergebnis, Ziel und Folgevektoren und deren Aggregate geschrieben  */
/* werden                                                            */
/* ***************************************************************** */                             
typedef FILE file;     /* fuer ESL                                   */
file *runreport;       /* Programmablaufskontrolldatei               */
file *konfig;          /* Modellkonfigurationsdatei                  */
/* ***************************************************************** */
/*                                                                   */
/*  Globale Konstanten und Variable fuer den Simulationsablauf       */
/*                                                                   */
/* ***************************************************************** */
int sl; /* Laenge der Einzelsimulation (RUN) in Perioden             */
int al; /* Anzahl der sukzessiven Simulationslaeufe (SET)            */
int rl = 1  ; /* Zaehlvariable fuer den laufenden SET                */
/* jumpback wird in Init() nach dem Oeffnen der Protokoldateien auf  */
/* Null gesetzt und in Fini() vor dem Ruecksprung in Init() auf Eins */
/* gesetzt um ein wiederholtes Oeffnen der Protokoldateien zu        */
/* verhindern                                                        */
int jumpback=0;
int gOwnnr;/* fuer Uebergabe von Ownnr() an indirekt aufgerufene acts*/
int gperiod;/* Globale ESL-Variablen der diskreten Simulationsuhrzeit*/
int glogtime;/* IMMER benutzt, statt period und logtime von ESL      */
long int gmem; /* Bytesanzahl des dynamischen angeforderten Speichers*/
/* Wird gesetzt, wenn Konfiguration aus Datei geladen sind           */
int load=0; /* [0] = nicht geladen, [1] = geladen                    */
/* ***************************************************************** */
/*                                                                   */
/* Definitionen und Strukturen fuer die dynamische Subjektverwaltung */
/*                                                                   */
/* ***************************************************************** */
int akvu; /* Anzahl der aktivierten VU                               */
int akvn; /* Anzahl der aktivierten VN                               */
int aktiVU[MAXVU+1]; /* Vektor der aktivierten VUs                   */
int aktiVN[MAXVN+1]; /* Vektor der aktivierten VN                    */
/* 0 : nicht aktiviert, 1 : aktiviert und vordefiniert               */
/* 2 = nicht aktiviert und vordefiniert,d.h. werden spaeter aktiviert*/
/* 3 = aktiviert und editierbar                                      */
/* ACHTUNG: NUR wenn aktiV_[_] <> 0 ist darf zu Beginn der Simulation*/
/*          Speicher fuer das Subjekt angefordert werden             */
/* ***************************************************************** */
/* Datenstruktur fuer die Zuordnung einer Verhaltenregel zu einem    */
/* ESL-Subjekt. Wird von den Strategiedaemonen der dynamischen       */
/* Subjektklassen VU und VN benoetigt.                               */
/* ***************************************************************** */   
typedef struct s0
{
  int  st;    /* Nummer der Verhaltensregel,  die ausgefuehrt wird   */
  int  lt;    /* Logischer Zeitpunkt der Ausfuehrung                 */
} ACTION;
/* ***************************************************************** */
/* Zuordnungstabellen fuer die Verhaltensregeln (Aggregat II) zu den */
/* Regelklassen (Aggregat III)  und die Zuordnung der Verhaltens-    */
/* regeln zu ihren Namen                                             */
/* ***************************************************************** */
int vkrvu[11] = {0,1,1,2,2,2,2,3,3,3,0}; /* Zuordnung von Verhaltens-*/
int vkrvn[8]  = {0,1,1,2,2,3,3,0}; /* regel und Verhaltensklasse     */
static char *vrvunm[] = { "VR(0): unbesetzt ", "Zufall I         ",
			  "Zufall II        ", "Mark Up I        ",
			  "Mark Up II       ", "Mark Up III      ",
			  "Erwartungsschaden", "Dumping          ",
			  "Durchschnitt     ", "Angriff          ",
			  "VR(10): unbesetzt" };
static char *vrvnnm[] = { "VR(0): unbesetzt ", "Zufall I         ",
			  "Zufall II        ", "Praeferenz       ",
			  "Totale Erinnerung", "Suche            ",
			  "Beste Information", "VR(7): unbesetzt " } ;
/* ***************************************************************** */
/* Zuordnungstabellen der Dateinamen der Aggregatdateien und         */
/* Initialisierung der Aggregattabellen. Ist ein Element dieser      */
/* Tabellen=1, dann wird die zugehoerige Aggregatdatei erzeugt.      */
/* ***************************************************************** */
static char *agvu1nm[] = { /*Datei-Namenstabelle Aggregat I der VUs  */
"imsvu000.dat",
"imsvu001.dat","imsvu002.dat","imsvu003.dat","imsvu004.dat",
"imsvu005.dat","imsvu006.dat","imsvu007.dat","imsvu008.dat",
"imsvu009.dat","imsvu010.dat","imsvu011.dat","imsvu012.dat",
"imsvu013.dat","imsvu014.dat","imsvu015.dat","imsvu016.dat",                                                            
"imsvu017.dat","imsvu018.dat","imsvu019.dat","imsvu020.dat",
"imsvu021.dat","imsvu022.dat","imsvu023.dat","imsvu024.dat",
"imsvu025.dat"
};
int agvu1[26] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
static char *agvu2nm[] = { /*Datei-Namenstabelle Aggregat II der VUs */
"imsvur00.dat",
"imsvur01.dat","imsvur02.dat","imsvur03.dat","imsvur04.dat",
"imsvur05.dat","imsvur06.dat","imsvur07.dat","imsvur08.dat",
"imsvur09.dat","imsvur10.dat"
};            
int agvu2[11] = {0,0,0,0,0,0,0,0,0,0,0};
static char *agvu3nm[] = { /*Datei-Namenstabelle Aggregat III der VUs*/
"imsvuvk0.dat","imsvuvk1.dat","imsvuvk2.dat","imsvuvk3.dat"
};                                      
int agvu3[4] = {0,0,0,0};
static char *agvu4nm[] = { /*Datei-Namenstabelle Aggregat IV der VUs */
"imsvusk0.dat","imsvusk1.dat"
};                       
int agvu4[2] = {0,0};
static char *agvn1nm[] = { /*Datei-Namenstabelle Aggregat I der VNs  */
"imsvn000.dat",
"imsvn001.dat","imsvn002.dat","imsvn003.dat","imsvn004.dat",               
"imsvn005.dat","imsvn006.dat","imsvn007.dat","imsvn008.dat",
"imsvn009.dat","imsvn010.dat","imsvn011.dat","imsvn012.dat",
"imsvn013.dat","imsvn014.dat","imsvn015.dat","imsvn016.dat",               
"imsvn017.dat","imsvn018.dat","imsvn019.dat","imsvn020.dat",
"imsvn021.dat","imsvn022.dat","imsvn023.dat","imsvn024.dat",
"imsvn025.dat","imsvn026.dat","imsvn027.dat","imsvn028.dat",
"imsvn029.dat","imsvn030.dat","imsvn031.dat","imsvn032.dat",
"imsvn033.dat","imsvn034.dat","imsvn035.dat","imsvn036.dat",             
"imsvn037.dat","imsvn038.dat","imsvn039.dat","imsvn040.dat",
"imsvn041.dat","imsvn042.dat","imsvn043.dat","imsvn044.dat",
"imsvn045.dat","imsvn046.dat","imsvn047.dat","imsvn048.dat",               
"imsvn049.dat","imsvn050.dat","imsvn051.dat","imsvn052.dat",
"imsvn053.dat","imsvn054.dat","imsvn055.dat","imsvn056.dat",
"imsvn057.dat","imsvn058.dat","imsvn059.dat","imsvn060.dat",
"imsvn061.dat","imsvn062.dat","imsvn063.dat","imsvn064.dat",
"imsvn065.dat","imsvn066.dat","imsvn067.dat","imsvn068.dat",               
"imsvn069.dat","imsvn070.dat","imsvn071.dat","imsvn072.dat",
"imsvn073.dat","imsvn074.dat","imsvn075.dat","imsvn076.dat",
"imsvn077.dat","imsvn078.dat","imsvn079.dat","imsvn080.dat",               
"imsvn081.dat","imsvn082.dat","imsvn083.dat","imsvn084.dat",
"imsvn085.dat","imsvn086.dat","imsvn087.dat","imsvn088.dat",
"imsvn089.dat","imsvn090.dat","imsvn091.dat","imsvn092.dat",
"imsvn093.dat","imsvn094.dat","imsvn095.dat","imsvn096.dat",
"imsvn097.dat","imsvn098.dat","imsvn099.dat","imsvn100.dat",               
"imsvn101.dat","imsvn102.dat","imsvn103.dat","imsvn104.dat",
"imsvn105.dat","imsvn106.dat","imsvn107.dat","imsvn108.dat",
"imsvn109.dat","imsvn110.dat","imsvn111.dat","imsvn112.dat",               
"imsvn113.dat","imsvn114.dat","imsvn115.dat","imsvn116.dat",
"imsvn117.dat","imsvn118.dat","imsvn119.dat","imsvn120.dat",
"imsvn121.dat","imsvn122.dat","imsvn123.dat","imsvn124.dat",
"imsvn125.dat","imsvn126.dat","imsvn127.dat","imsvn128.dat",
"imsvn129.dat","imsvn130.dat","imsvn131.dat","imsvn132.dat",               
"imsvn133.dat","imsvn134.dat","imsvn135.dat","imsvn136.dat",
"imsvn137.dat","imsvn138.dat","imsvn139.dat","imsvn140.dat",
"imsvn141.dat","imsvn142.dat","imsvn143.dat","imsvn144.dat",               
"imsvn145.dat","imsvn146.dat","imsvn147.dat","imsvn148.dat",
"imsvn149.dat","imsvn150.dat","imsvn151.dat","imsvn152.dat",
"imsvn153.dat","imsvn154.dat","imsvn155.dat","imsvn156.dat",
"imsvn157.dat","imsvn158.dat","imsvn159.dat","imsvn160.dat",
"imsvn161.dat","imsvn162.dat","imsvn163.dat","imsvn164.dat",               
"imsvn165.dat","imsvn166.dat","imsvn167.dat","imsvn168.dat",
"imsvn169.dat","imsvn170.dat","imsvn171.dat","imsvn172.dat",
"imsvn173.dat","imsvn174.dat","imsvn175.dat","imsvn176.dat",               
"imsvn177.dat","imsvn178.dat","imsvn179.dat","imsvn180.dat",
"imsvn181.dat","imsvn182.dat","imsvn183.dat","imsvn184.dat",
"imsvn185.dat","imsvn186.dat","imsvn187.dat","imsvn188.dat",
"imsvn189.dat","imsvn190.dat","imsvn191.dat","imsvn192.dat",
"imsvn193.dat","imsvn194.dat","imsvn195.dat","imsvn196.dat",
"imsvn197.dat","imsvn198.dat","imsvn199.dat","imsvn200.dat"
};
int agvn1[201] = {0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0                                                                      
};
static char *agvn2nm[] = { /*Datei-Namenstabelle Aggregat II der VNs */
"imsvnr00.dat",
"imsvnr01.dat","imsvnr02.dat","imsvnr03.dat","imsvnr04.dat",
"imsvnr05.dat","imsvnr06.dat","imsvnr07.dat"
};                                      
int agvn2[8] = {0,0,0,0,0,0,0,0};
static char *agvn3nm[] = { /*Datei-Namenstabelle Aggregat III der VNs*/
"imsvnvk0.dat","imsvnvk1.dat","imsvnvk2.dat","imsvnvk3.dat"
};
int agvn3[4] = {0,0,0,0};
static char *agvn4nm[] = { /*Datei-Namenstabelle Aggregat IV der VNs */
"imsvnsk0.dat","imsvnsk1.dat"
};                       
int agvn4[2] = {0,0};
/* ***************************************************************** */
/* class VU: Definition der Sub-Datenstrukturen der beiden Sparten.  */
/*           Die Umsetzung der Variable erfolgt nach der Definition: */
/*           Zielvektor, Ergebnisvektor, Folgevektor.                */
/* ***************************************************************** */
typedef struct s11        /* Spartendefinition: Sparte 1             */
{
  float  Pr[SIMLAENGE+1]; /* Zielvektor: Praemie in Periode t        */
  float  Wa[SIMLAENGE+1]; /* Zielvektor: Werbeaufwand in Periode t   */
  float  Rs[SIMLAENGE+1]; /* Ergebnisv.: Schadenreserven in Periode t*/
  int    Vn[SIMLAENGE+1]; /* Ergebnisv.: Anzahl der Versicherten     */
  int    Sa[SIMLAENGE+1]; /* Folgevektr: Schadenanzahl in Periode t  */
  float  Sh[SIMLAENGE+1]; /* Folgevektr: Schadensumme in Periode t   */
} LV;
typedef struct s12        /* Spartendefinition: Sparte 2             */
{
  float  Pr[SIMLAENGE+1]; /* Zielvektor: Praemie in Periode t        */
  float  Wa[SIMLAENGE+1]; /* Zielvektor: Werbeaufwand in Periode t   */
  float  Rs[SIMLAENGE+1]; /* Ergebnisv.: Schadenreserven in Periode t*/
  int    Vn[SIMLAENGE+1]; /* Ergebnisv.: Anzahl der Versicherten     */
  int    Sa[SIMLAENGE+1]; /* Folgevektr: Schadenanzahl in Periode t  */
  float  Sh[SIMLAENGE+1]; /* Folgevektr: Schadensumme in Periode t   */
} KV;
typedef union u1    /* Strukturvariablen der Gesamtspartenstruktur   */
{
 int   type; /* fuer Identifierung bei Speichern/Laden der Daten     */
 LV    l; /* Sparte 1 */
 KV    k; /* Sparte 2 */
} SPARTE;
/* ***************************************************************** */
/*                                                                   */
/*                  classVU: Die Versicherer                         */
/*                                                                   */
/* ***************************************************************** */
typedef struct s1
{ 
  int    Ap;              /* Aktivierungsperiode                     */
  int    Al[SIMLAENGE+1]; /* Aktivierungslauf                        */
  float  A1[4];           /* Anspruchniveaus: Sparte 1               */
  float  A2[4];           /* Anspruchniveaus: Sparte 2               */
  float  Pv[16];          /* IMS-Paramtervektor der Versicherungen   */
			  /*(a,b,c,d,e,f,g,h,a*,b*,c*,d*,e*,f*,g*,h*)*/
  int    Pa[24];          /* =1, wenn Pv[i] in der Parametermaske    */
			  /* abgefragt werden soll. [0..15] fuer PV, */
			  /* [16..19] fuer A1[], [20..23] fuer A2[]  */
  int    Vr;              /* Nummer der Verhaltensregel: VU: 1..9    */
  int    Vk;              /* Regelklasse fuer Aggregatbildung:1,2,3  */
  ACTION Ac[MAXNLOG+1];   /* Zuordnung der Verhaltensregeln          */
  SPARTE Sp[MAXSPARTEN+1];/* Sparte 1 und 2 zusammengefasst          */
} classVU;
/* ***************************************************************** */
/* class VN: Definition der Sub-Datenstrukturen der beiden Sparten.  */
/*           Die Umsetzung der Variable erfolgt nach der Definition: */
/*           Zielvektor, Ergebnisvektor, Folgevektor.                */
/* ***************************************************************** */           
typedef struct s21       /* Risiko 1                                 */
{
 int    Vu[SIMLAENGE+1]; /* Zielvektor: Anbieternummer, 0=eigenvers. */
 int    Vs[SIMLAENGE+1]; /* Zielvektor: Versicherungsstatus in t     */
 float  Vp[SIMLAENGE+1]; /* Ergebnisv.: Gezahlte Praemie in t        */
 float  Ev[SIMLAENGE+1]; /* Ergebnisv.: Eigenversichert.Schaden in t */
 float  Sw[SIMLAENGE+1]; /* Folgevektr: Schadenwahrscheinlichk. in t */
 float  Sh[SIMLAENGE+1]; /* Folgevektr: Schadenhoehe in t            */ 
 float  Pf[MAXVU+1];     /* Hilfsvektr: Anbieterpraeferenz in t      */
} RISKLV;                                                          
typedef struct s22       /* Risiko 2                                 */
{
 int    Vu[SIMLAENGE+1]; /* Zielvektor: Anbieternummer, 0=eigenvers. */
 int    Vs[SIMLAENGE+1]; /* Zielvektor: Versicherungsstatus in t     */
 float  Vp[SIMLAENGE+1]; /* Ergebnisv.: Gezahlte Praemie in t        */
 float  Ev[SIMLAENGE+1]; /* Ergebnisv.: Eigenversichert.Schaden in t */
 float  Sw[SIMLAENGE+1]; /* Folgevektr: Schadenwahrscheinlichk. in t */
 float  Sh[SIMLAENGE+1]; /* Folgevektr: Schadenhoehe in t            */ 
 float  Pf[MAXVU+1];     /* Hilfsvektr: Anbieterpraeferenz in t      */
} RISKKV;
typedef union u2      /* Strukturvariable der Gesamtrisikostruktur   */
{               
 int     type; /* wichtig fuer laden und speichern                   */
 RISKLV  l;
 RISKKV  k;
} RISIKO;
/* ***************************************************************** */
/*                                                                   */
/*              classVN: Die Versicherungsnehmer                     */
/*                                                                   */
/* ***************************************************************** */
typedef struct s2
{
 int    Ap;                 /* Aktivierungsperiode                   */
 int    Al[SIMLAENGE+1];    /* Aktivierungslauf                      */ 
 int    Vr;                 /* Nummer der Verhaltensregel: 1..9,VN   */
 int    Vk;                 /* Regelklasse: Aggregatbildung: 1,2,3   */
 float  Vm[SIMLAENGE+1];    /* Vermoegen des Versicherten in t       */ 
 float  Pv[16];             /* IMS-Paramtervektor der                */
    /* Versicherungsnehmer: (a,b,c,d,e,f,g,h,a*,b*,c*,d*,e*,f*,g*,h*)*/
 int    Pa[16];             /* =1, wenn Pv[i] in der Parametermaske  */
			    /* abgefragt werden soll. [0..15] fuer PV*/
 ACTION Ac[MAXNLOG+1];      /* Zuordnung der Verhaltensregeln        */
 RISIKO Rk[MAXRISKS+1];     /* Zusammengefasste Risiken              */
} classVN;                                                                                                              
/* ***************************************************************** */
/*                                                                   */
/*               classBAV: Der Informationsverteiler                 */
/*                                                                   */
/* ***************************************************************** */                                                                 
typedef struct s7
{
 int   As[SIMLAENGE+1];/* Aenderungsschockindikator:0,1=Schock in t  */
 int   Ar[SIMLAENGE+1];/*  " fuer die Sim.runs, d.h. Ar[50]=0,Ar[51] */
		       /* = 1: kein Aenderungsschock im 50.ten Lauf  */
		       /* aber Aenderungsschock im 51.ten Lauf       */
		       /* -> Aenderungsschock ist: wenn              */
		       /* Ar[gperiod] * As[sl] = 1 ist !             */
 int   Rp;             /* = 1, wenn Wiederholungen zugelassen sind   */
                       /* wird in func Starts() abgefragt, sonst 0 ! */                       
 float Zs[SIMLAENGE+1];/* Zur Verzinsung der VU-Reserven             */
 float Sk[SIMLAENGE+1];/* Kosten fuer EINE Praemieninfo. eines VUs   */
		       /* **** Vektoren fuer die Aggregatverwaltung* */
 int   Vuag1[MAXVU+1]; /* = 1, wenn VUxy in der Periode t aktiv war  */
		       /* -> akvu = Anzahl in t aktiver VUs          */
 int   Vuag2[11];      /* wieviel VUs mit Regel i in t aktiv waren   */                    
 int   Vuag3[4];       /* wieviel in Regelklasse j in t aktiv waren  */
 int   Vnag1[MAXVN+1]; /* = 1, wenn VNxy in Periode t aktiv war      */
		       /* -> akvn = Anzahl in t aktiver VNs          */ 
 int   Vnag2[8];       /* wieviele VNs mit Regel i in t aktiv waren  */
 int   Vnag3[4];       /* wieviele in Regelklasse j in t aktiv waren */
		       /* Subjektvektoren fuer die Aggregatbildung   */
		       /* **** Vektoren fuer die Fremdinformation ** */
		       /* VU: VR DUMPING                             */
 float Pm[MAXSPARTEN]; /* Minimale Praemie in Sparte i in t-1        */
 float Wm[MAXSPARTEN]; /* Maximale Werbung in Sparte i in t-1        */ 
		       /* VU: VR: DURCHSCHNITT                       */
 float Dp[MAXSPARTEN]; /* Durchschnittspraemie der Sparten in t      */
 float Dw[MAXSPARTEN]; /* Durchschnittlicher Werbeaufwand, Sparte,t-1*/
		       /* VU: VR ANGRIFF                             */
 float Mp[MAXSPARTEN]; /* Praemien des Marktfuehrers(max. Reserven)  */
 float Mw[MAXSPARTEN]; /* Werbeaufwendungen des Marktfuehrers        */
		       /* VN: alle VR:                               */ 
 float Dg[MAXRISKS];   /* Durchschnittlicher Versicherungsgrad in t-1*/
} classBAV;
								       

'''