include make_opts

LIBDIR= ../lib/
BINDIR= ../bin/
PDFDIR= ./PDF/

PROCESS= hfill.o matrix.o myamp.o 

HBOOK = hfill.o hcurve.o hbook1.o hbook2.o

GENERIC = $(alfas_functions).o invarients.o hfill.o pawgraphs.o ran1.o rw_events.o rw_routines.o kin_functions.o \
	  open_file.o basecode.o setrun.o run_printout.o dgauss.o ranmar.o getissud.o

INCLUDEF= coupl.inc genps.inc hbook.inc psample.inc pmass.inc nexternal.inc cluster.inc

BANNER  =  write_banner.o  rw_events.o ranmar.o  kin_functions.o open_file.o  rw_routines.o alfas_functions.o

COMBINE = combine_events.o  rw_events.o ranmar.o  kin_functions.o open_file.o rw_routines.o alfas_functions.o setrun.o



.f.o: ; $(FC) $(FFLAGS) -c $*.f

all: $(LIBDIR)libdhelas.a $(LIBDIR)libgeneric.a $(LIBDIR)libpdf.a  $(LIBDIR)libmodel.a  $(LIBDIR)libcernlib.a \
    param_card.inc
	rm -f PDF/*.o

scaled.dat:
	combine_events

$(BINDIR)sum_html: sum_html.o 
	$(FC) $(FFLAGS) -o sum_html sum_html.o   
	mv sum_html $(BINDIR)

$(LIBDIR)libdhelas.a: DHELAS
	rm -f $(LIBDIR)libdhelas.a
	cd DHELAS; make

$(LIBDIR)libgeneric.a: $(GENERIC)
	rm -f $(LIBDIR)libgeneric.a
	ar cru libgeneric.a $(GENERIC)
	ranlib libgeneric.a
	mv libgeneric.a $(LIBDIR)
	rm -f $(alfas_functions).o 

setrun.o: run_card.inc 
	$(FC) $(FFLAGS) -c -o setrun.o setrun.f

$(LIBDIR)libpdf.a: PDF
	rm -f $(LIBDIR)libpdf.a
	cd PDF; make	

$(LIBDIR)libcernlib.a: CERNLIB
	rm -f $(LIBDIR)libcernlib.a
	cd CERNLIB; make	

$(LIBDIR)libmodel.a: MODEL param_card.inc
	rm -f $(LIBDIR)libmodel.a
	cd MODEL; make	

genps.inc: nexternal.inc
	touch genps.inc

run_card.inc: ../Cards/run_card.dat
	../bin/aMCatNLO treatcards run

param_card.inc: ../Cards/param_card.dat
	../bin/aMCatNLO treatcards param

$(BINDIR)gen_ximprove: gen_ximprove.o ranmar.o rw_routines.o open_file.o
	$(FC) $(FFLAGS) -o gen_ximprove gen_ximprove.o ranmar.o rw_routines.o open_file.o
	mv gen_ximprove $(BINDIR)

$(BINDIR)combine_events: $(COMBINE)
	$(FC) $(FFLAGS) -o combine_events $(COMBINE) $(LIBDIR)/libmodel.a $(LIBDIR)/libpdf.a 
	mv combine_events $(BINDIR)

clean4pdf:
	rm -f ../lib/libpdf.a
	rm -f ../lib/libgeneric.a

clean:
	rm -f *.o
	rm -f param_card.inc run_card.inc
	cd MODEL; make clean
	cd CERNLIB; make clean; cd ..
	cd PDF; make clean
	cd DHELAS; make clean
	rm -f $(BINDIR)/combine_events $(BINDIR)/gen_ximprove