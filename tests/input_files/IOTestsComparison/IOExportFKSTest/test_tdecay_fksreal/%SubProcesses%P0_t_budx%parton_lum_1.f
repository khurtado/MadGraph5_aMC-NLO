      SUBROUTINE DLUM_1(LUM)
C     ****************************************************            
C         
C     Generated by MadGraph5_aMC@NLO v. %(version)s, %(date)s
C     By the MadGraph5_aMC@NLO Development Team
C     Visit launchpad.net/madgraph5 and amcatnlo.web.cern.ch
C     RETURNS PARTON LUMINOSITIES FOR MADFKS                          
C        
C     
C     Process: t > b u d~ g QED<=2 QCD+2*QED<=5 [ real = QCD ]
C     Process: t > b c s~ g QED<=2 QCD+2*QED<=5 [ real = QCD ]
C     
C     ****************************************************            
C         
      IMPLICIT NONE
C     
C     CONSTANTS                                                       
C         
C     
      INCLUDE 'genps.inc'
      INCLUDE 'nexternal.inc'
      DOUBLE PRECISION       CONV
      PARAMETER (CONV=389379660D0)  !CONV TO PICOBARNS             
C     
C     ARGUMENTS                                                       
C         
C     
      DOUBLE PRECISION PP(0:3,NEXTERNAL), LUM
C     
C     LOCAL VARIABLES                                                 
C         
C     
      INTEGER I, ICROSS,ITYPE,LP
      DOUBLE PRECISION P1(0:3,NEXTERNAL)

      DOUBLE PRECISION XPQ(-7:7)
C     
C     EXTERNAL FUNCTIONS                                              
C         
C     
      DOUBLE PRECISION ALPHAS2,REWGT,PDG2PDF
C     
C     GLOBAL VARIABLES                                                
C         
C     
      INTEGER              IPROC
      DOUBLE PRECISION PD(0:MAXPROC)
      COMMON /SUBPROC/ PD, IPROC
      INCLUDE 'coupl.inc'
      INCLUDE 'run.inc'
      INTEGER IMIRROR
      COMMON/CMIRROR/IMIRROR
C     
C     DATA                                                            
C         
C     

      DATA ICROSS/1/
C     ----------                                                      
C         
C     BEGIN CODE                                                      
C         
C     ----------                                                      
C         
      LUM = 0D0
      IF (IMIRROR.EQ.2) THEN
        PD(0) = 0D0
        IPROC = 0
        IPROC=IPROC+1  ! t > b u d~ g
        PD(IPROC) = 1D0

        PD(0)=PD(0)+PD(IPROC)
        IPROC=IPROC+1  ! t > b c s~ g
        PD(IPROC) = 1D0

        PD(0)=PD(0)+PD(IPROC)
      ELSE
        PD(0) = 0D0
        IPROC = 0
        IPROC=IPROC+1  ! t > b u d~ g
        PD(IPROC) = 1D0

        PD(0)=PD(0)+PD(IPROC)
        IPROC=IPROC+1  ! t > b c s~ g
        PD(IPROC) = 1D0

        PD(0)=PD(0)+PD(IPROC)
      ENDIF
      DO I=1,IPROC
        IF (NINCOMING.EQ.2) THEN
          LUM = LUM + PD(I) * CONV
        ELSE
          LUM = LUM + PD(I)
        ENDIF
      ENDDO
      RETURN
      END

