#!/usr/bin/perl
# geschrieben für/auf M$ Windows XP SP2 mit Perl v5.8.2,
# aber ich bin ganz sicher dass es sich in nullkommanix auf
# andere betriebssysteme portieren lässt :)
# getestet mit FritzBox SL WLAN 3020 mit 1&1 Branding und Firmware 09.03.87 & 09.04.07
# keine ahnung ob es auch mit anderen boxen funktioniert...
#
# Umgeschrieben auf/für Unix, Unix klappt, Windows sollte auch klappen :)
# 21.05.2008 anpass fuer ..57 version
# 18.10.2009 anpass fuer ..76 version
# 01.05.2014 anpass fuer neue box und rpi

use POSIX;

# Hier ggf ein bisschen modifizieren

# Hier nichts mehr ändern

chdir  '/disk/software/local/lib/fritzphp';
my $response=`php ./fritzbox_dsldata.php `;

#@antwort = split(/\n/,$response);
@antwort = split(/<\/tr>/,$response);
$match=0;
foreach $zeile (@antwort) {
#print "bbbb $zeile bbb\n";
	if ( $zeile =~ /"c1">Leitungskapazit/ ) {
		$match++;
		$mode=1;
        }
	if ( $zeile =~ />DSLAM-Datenrate Max/ ) {
		$match++;
		$mode=2;
        }
	if ( $zeile =~ /Aktuelle.Datenrate/ ) {
		$match++;
		$mode=3;
        }
	if ( $zeile =~ /="c1">St.+rabstandsmarge/ ) {
		$match++;
		$mode=4;
        }
	if ( $zeile =~ /Leitungs.+mpfung/ ) {
		$match++;
		$mode=5;
        }
	if ( $zeile =~ />DSLAM-Datenrate Min/ ) {
		$match++;
		$mode=6;
        }
	if ( $zeile =~ /Latenz/ ) {
		$match++;
		$mode=7;
        }
	if ( $zeile =~ /rungsschutz/ ) {
		$match++;
		$mode=8;
	}
#print "xxx $zeile xxx\n" if ( $match == 0 );
#print "--- $zeile ---\n" if ( $match != 0 );
	if ( $match == 1 ) {
		if ( ($zeile =~ /<td .+class="c3">([0-9]+)<\/td>.+class="c4">([0-9]+)<\/td>/) && $mode == 1 ) {
			$lki = $1; $lko = $2;
		}
		if ( ($zeile =~ /<td .+class="c3">([0-9]+)<\/td>.+class="c4">([0-9]+)<\/td>/) && $mode == 2 ) {
			$dslmaxi = $1; $dslmaxo = $2;
		}
		if ( ($zeile =~ /<td .+class="c3">([0-9]+)<\/td>.+class="c4">([0-9]+)<\/td>/) && $mode == 3 ) {
			$nutzi = $1; $nutzo = $2 ;
		}
		if ( ($zeile =~ /<td .+class="c3">([0-9]+)<\/td>.+class="c4">([0-9]+)<\/td>/) && $mode == 4 ) {
			$sri = $1; $sro = $2;
		}
		if ( ($zeile =~ /<td .+class="c3">([0-9]+)<\/td>.+class="c4">([0-9]+)<\/td>/) && $mode == 5 ) {
			$ldi = $1; $ldo =  $2;
		}
		if ( ($zeile =~ /<td .+class="c3">([0-9]+)<\/td>.+class="c4">([0-9-]+)<\/td>/) && $mode == 6 ) {
			$dslmini = $1; $dslmino = $2;
			if ( $dslmino == '-' ) {
				$dslmino = 0;
			}
		}
		if ( ($zeile =~ /<td .+class="c3">([0-9]+) ms<\/td>.+class="c4">([0-9]+) ms<\/td>/) && $mode == 7 ) {
			$latenzi = $1; $latenzo = $2;
		}
		if ( ($zeile =~ /<td .+class="c3">([0-9]+) ms<\/td>.+class="c4">fast<\/td>/) && $mode == 7 ) {
			$latenzi = $1; $latenzo = 0
		}
		if ( ($zeile =~ /<td .+class="c3">fast<\/td>.+class="c4">([0-9]+) ms<\/td>/) && $mode == 7 ) {
			$latenzi = 0; $latenzo = $1;
		}
		if ( ($zeile =~ /<td .+class="c3">fast<\/td>.+class="c4">fast<\/td>/) && $mode == 7 ) {
			$latenzi = 0; $latenzo = 0;
		}
		if ( ($zeile =~ /<td .+class="c3">([0-9]+)<\/td>.+class="c4">([0-9]+)<\/td>/) && $mode == 8 ) {
			$impin = $1; $impout = $2;
		}
  		$match = 0;
	}
	#print $match."---".$mode."-".$counter."<".$zeile."\n";
}
print "fritzdsl leitungin=".$lki*1024 .",leitungout=".$lko*1024 .
      ",dslmaxin=".$dslmaxi*1024 .",dslmaxout=".$dslmaxo*1024 .
      ",dslminin=".$dslmini*1024 .",dslminout=".$dslmino*1024 .
      ",nutzin=".$nutzi*1024 .",nutzout=".$nutzo*1024 .
      ",snin=".$sri.",snout=".$sro.
      ",dmpin=".$ldi.",dmpout=".$ldo.
      ",latenzin=". $latenzi.",latenzout=".$latenzo.
      ",inpin=".$impin.",inpout=".$impout;
